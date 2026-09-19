import os
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
    "Eres un CLI parser para administración de sistemas y desarrollo. "
    "Devuelve ÚNICAMENTE el comando completo y directamente ejecutable en la terminal en texto plano puro "
    "(por ejemplo: 'nmap -oN salida.txt <objetivo>', NUNCA devuelvas solo una bandera aislada como '-oN'). "
    "Sin comillas, sin backticks (`) y sin bloques markdown. Cero explicaciones, cero saludos. Sé directo."
)


def ask_model(prompt: str, context: str = ""):
    """
    Envía la solicitud al LLM utilizando streaming.
    Mantiene el SYS_PROMPT estático en el mensaje system para maximizar el KV-cache (Prompt Caching)
    e inyecta el contexto relevante dentro del turno del usuario.
    """
    if context:
        user_content = f"--- CONTEXTO RELEVANTE (NOTAS LOCALES) ---\n{context}\n------------------------------------------\nORDEN: {prompt}"
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


def get_engine_info() -> dict:
    """Retorna información del cliente configurado."""
    return {
        "base_url": BASE_URL,
        "model": MODEL,
        "is_local": any(host in BASE_URL.lower() for host in ("11434", "localhost", "127.0.0.1"))
    }