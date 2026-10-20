import os
import json
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from typing import List, Dict, Tuple, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Resolución absoluta para garantizar que el archivo .env se cargue desde la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env", override=True)

BASE_URL = os.environ.get("OPENAI_BASE_URL", "http://localhost:11434/v1")
API_KEY = os.environ.get("OPENAI_API_KEY", "ollama")
MODEL = os.environ.get("OPENAI_MODEL", "llama3")

# Timeout por defecto para llamadas a la API (en segundos)
REQUEST_TIMEOUT = float(os.environ.get("OPENAI_TIMEOUT", "30.0"))

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
    timeout=REQUEST_TIMEOUT
)

SYS_PROMPT = (
    "Eres un CLI parser estricto para administración de sistemas y desarrollo. "
    "Devuelve ÚNICAMENTE el comando completo y directamente ejecutable en la terminal. "
    "Debes incluir siempre el binario, opciones y argumentos necesarios. "
    "NUNCA devuelvas únicamente un flag o modificador aislado. "
    "Responde estrictamente en texto plano puro, sin comillas, sin backticks (`) y sin formato markdown. "
    "Cero explicaciones, cero saludos. Sé directo."
)


def _is_local_endpoint(url: str) -> bool:
    """Verifica si la URL apunta a un servidor local (Ollama / llama.cpp)."""
    try:
        parts = urlsplit(url)
        hostname = (parts.hostname or "").lower()
        port = parts.port
        return (
            hostname in ("localhost", "127.0.0.1", "::1")
            or port == 11434
            or "11434" in url
        )
    except Exception:
        return False


def ask_model(prompt: str, context: str = ""):
    """
    Envía la solicitud al LLM utilizando streaming.
    Mantiene el SYS_PROMPT estático en el mensaje system para maximizar el KV-cache (Prompt Caching)
    e inyecta el contexto relevante dentro del turno del usuario.
    """
    if context:
        user_content = (
            f"--- NOTAS LOCALES DE REFERENCIA ---\n"
            f"{context}\n"
            f"-----------------------------------\n"
            f"Usa las notas locales si contienen la respuesta. Si la orden pide algo que no está en las notas, "
            f"construye el comando correcto con tu conocimiento general.\n"
            f"ORDEN: {prompt}"
        )
    else:
        user_content = prompt

    messages = [
        {"role": "system", "content": SYS_PROMPT},
        {"role": "user", "content": user_content}
    ]

    # Optimizaciones específicas para Ollama en inferencia local
    is_local = _is_local_endpoint(BASE_URL)
    extra_body = {
        "options": {
            "num_ctx": 4096,
            "repeat_penalty": 1.1,  # Previene repeticiones de flags o bucles en modelos pequeños
            "temperature": 0.1,
        }
    } if is_local else None

    return client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.1,
        max_tokens=400,
        stream=True,
        stop=["<|im_end|>", "<|endoftext|>", "```\n\n", "ORDEN:", "\n\n\n\n"],
        extra_body=extra_body
    )


def explain_command(command: str):
    """Genera una explicación breve y concisa de los parámetros y banderas de un comando."""
    explain_prompt = (
        "Eres un experto en terminales y administración de sistemas. "
        "Explica de forma muy breve y clara qué hace el siguiente comando y desglosa sintéticamente cada una de sus banderas o argumentos:\n\n"
        f"Comando: {command}"
    )
    return client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": explain_prompt}],
        temperature=0.2,
        max_tokens=350,
        stream=True
    )


def set_model(new_model: str) -> str:
    """Cambia el modelo activo en tiempo de ejecución."""
    global MODEL
    MODEL = new_model.strip()
    return MODEL


def list_available_models() -> List[str]:
    """Consulta la API de Ollama para listar los modelos descargados localmente."""
    if not _is_local_endpoint(BASE_URL):
        return []

    try:
        parts = urlsplit(BASE_URL)
        tags_url = urlunsplit((parts.scheme or "http", parts.netloc, "/api/tags", "", ""))
        req = urllib.request.Request(tags_url, headers={"User-Agent": "Spectre-CLI"})
        with urllib.request.urlopen(req, timeout=3.0) as response:
            data = json.loads(response.read().decode())
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def get_engine_info() -> Dict[str, object]:
    """Retorna información del cliente configurado."""
    return {
        "base_url": BASE_URL,
        "model": MODEL,
        "is_local": _is_local_endpoint(BASE_URL)
    }
