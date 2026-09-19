import os
import json
import urllib.request
from openai import OpenAI
from dotenv import load_dotenv

# Forzar carga de variables desde .env para evitar conflictos con terminal/sistema
load_dotenv(override=True)

BASE_URL = os.environ.get("OPENAI_BASE_URL", "http://localhost:11434/v1")
API_KEY = os.environ.get("OPENAI_API_KEY", "ollama")
MODEL = os.environ.get("OPENAI_MODEL", "llama3")

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY
)

SYS_PROMPT = (
    "Eres un CLI parser estricto para administración de sistemas y desarrollo. "
    "Devuelve ÚNICAMENTE el comando completo y directamente ejecutable en la terminal. "
    "Debes incluir siempre el binario, opciones y argumentos necesarios. "
    "NUNCA devuelvas únicamente un flag o modificador aislado. "
    "Responde estrictamente en texto plano puro, sin comillas, sin backticks (`) y sin formato markdown. "
    "Cero explicaciones, cero saludos. Sé directo."
)


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

    # Optimizaciones específicas para Qwen2.5-Coder en inferencia local (Ollama)
    is_local = any(host in BASE_URL.lower() for host in ("11434", "localhost", "127.0.0.1"))
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


def list_available_models() -> list[str]:
    """Consulta la API de Ollama para listar los modelos descargados localmente."""
    is_local = any(host in BASE_URL.lower() for host in ("11434", "localhost", "127.0.0.1"))
    if not is_local:
        return []

    try:
        # La raíz de Ollama suele estar en http://localhost:11434
        root_url = BASE_URL.replace("/v1", "")
        tags_url = f"{root_url.rstrip('/')}/api/tags"
        req = urllib.request.Request(tags_url, headers={"User-Agent": "Spectre-CLI"})
        with urllib.request.urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode())
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def get_engine_info() -> dict:
    """Retorna información del cliente configurado."""
    return {
        "base_url": BASE_URL,
        "model": MODEL,
        "is_local": any(host in BASE_URL.lower() for host in ("11434", "localhost", "127.0.0.1"))
    }