# Spectre CLI ⚡

> **Asistente de sintaxis estricta y comandos de terminal para SysAdmins y Desarrolladores.**

Spectre es una herramienta minimalista y determinista diseñada para entregar comandos de terminal y fragmentos de código ejecutables sin saludos, explicaciones innecesarias ni bloques markdown. Cuenta con un motor **Micro-RAG** integrado para consultar notas locales de forma ultrarrápida sin sobrecargar la inferencia local.

---

## Características

- 🎯 **Sintaxis Estricta y Determinista**: Instrucción de sistema diseñada para devolver únicamente el comando ejecutable listo para terminal.
- ⚡ **Inferencia Rápida con Streaming**: Transmisión de tokens en tiempo real con latencia mínima.
- 🧠 **Motor Micro-RAG en Memoria**: Indexación inteligente de archivos en `payloads/` con búsqueda por relevancia y poda dinámica. Si una orden no requiere notas, inyecta 0 tokens.
- 🔄 **Hot-Reloading**: Detecta cambios en los archivos de `payloads/` automáticamente sin necesidad de reiniciar la sesión.
- 🔌 **Compatibilidad Universal**: Funciona tanto con modelos locales en **Ollama** (`Qwen2.5-Coder`, `Llama 3`, etc.) como proveedores remotos (**OpenRouter**, **OpenAI**).
- 🛡️ **Optimizado para Qwen2.5-Coder**: Ajustes finos de `repeat_penalty`, stop tokens de ChatML y formato en texto plano.

---

## Requisitos

- Python 3.10 o superior
- Ollama (opcional, para ejecución 100% local) o clave de API de OpenAI / OpenRouter

---

## Instalación

1. Clona este repositorio o descarga los archivos:
   ```bash
   git clone <url-del-repositorio>
   cd spectre
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configura tus variables de entorno:
   ```bash
   cp .env.example .env
   ```
   Edita `.env` según tu proveedor deseado:
   
   **Para Ollama Local:**
   ```env
   OPENAI_BASE_URL="http://localhost:11434/v1"
   OPENAI_API_KEY="ollama"
   OPENAI_MODEL="hf.co/bartowski/Qwen2.5-Coder-1.5B-Instruct-abliterated-GGUF"
   ```

   **Para OpenRouter:**
   ```env
   OPENAI_BASE_URL="https://openrouter.ai/api/v1"
   OPENAI_API_KEY="tu-clave-aqui"
   OPENAI_MODEL="meta-llama/llama-3.3-70b-instruct:free"
   ```

---

## Uso

Inicia la herramienta interactiva:

```bash
python main.py
```

### Comandos Internos

Dentro de la sesión interactiva puedes usar:

- `:status` - Muestra el modelo activo, endpoint y estadísticas de notas indexadas.
- `:reload` - Fuerza la reindexación de los archivos en `payloads/`.
- `:clear`  - Limpia la pantalla de la terminal.
- `:help`   - Muestra la ayuda de comandos internos.
- `:exit`   - Cierra la aplicación (o usa `Ctrl+C` / `Ctrl+D`).

---

## Base de Conocimiento Local (`payloads/`)

Puedes añadir cualquier archivo `.txt` o `.md` dentro de la carpeta `payloads/` (por ejemplo guías de comandos, rangos de IP, credenciales de laboratorio, cheatsheets). Spectre segmentará y buscará en estos archivos solo cuando la consulta sea relevante.

---

## Estructura del Proyecto

```
spectre/
├── .env.example        # Plantilla de variables de entorno
├── .gitignore          # Reglas de exclusión de git
├── ai_engine.py        # Motor de conexión e inferencia con OpenAI/Ollama
├── file_reader.py      # Micro-RAG: indexador, segmentador y buscador selectivo
├── main.py             # Interfaz CLI de terminal y bucle interactivo
├── payloads/           # Base de conocimiento local (.txt, .md)
│   ├── apuntes_redes.txt
│   └── guia_nmap.txt
├── README.md           # Documentación del proyecto
└── requirements.txt    # Dependencias de Python
```
