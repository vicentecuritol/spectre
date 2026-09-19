# Spectre CLI ⚡

> **Asistente de sintaxis estricta y comandos de terminal para SysAdmins y Desarrolladores.**

Spectre es una herramienta CLI minimalista y determinista diseñada para entregar comandos de terminal y fragmentos de código directamente ejecutables sin saludos, explicaciones innecesarias ni bloques markdown. Cuenta con un motor **Micro-RAG** integrado para consultar notas locales de forma ultrarrápida sin sobrecargar la inferencia local.

---

## Características Principales

- 🎯 **Sintaxis Estricta y Determinista**: Instrucción de sistema diseñada para devolver únicamente el comando ejecutable listo para terminal.
- ⚡ **Inferencia Rápida con Streaming**: Transmisión de tokens en tiempo real con latencia mínima.
- 📋 **Portapapeles Automático**: Copia inmediatamente el comando generado al portapapeles del sistema operativo (`Windows`, `macOS`, `Linux`) sin dependencias externas.
- 🚀 **Modo Directo (Single-Shot) & Interactivo**: Úsalo en una sola línea `python main.py "orden"` o en una sesión continua interactiva.
- 🧠 **Motor Micro-RAG en Memoria**: Indexación inteligente de archivos en `payloads/` con búsqueda por relevancia y poda dinámica. Si una orden no requiere notas, inyecta **0 tokens** (latencia 0 ms).
- 💡 **Modo Explicación (`:why`)**: Desglosa cada parámetro y bandera del último comando generado cuando necesitas entender su funcionamiento.
- 🛡️ **Ejecución Asistida Segura (`:exec`)**: Ejecuta el comando generado en tu terminal previa confirmación interactiva `[y/N]`.
- 🔄 **Gestión de Modelos en Caliente**: Lista (`:models`) y cambia (`:model <nombre>`) entre tus modelos locales de Ollama sin reiniciar la sesión.
- 🔌 **Compatibilidad Universal**: Funciona tanto con modelos locales en **Ollama** (`Qwen2.5-Coder`, `Llama 3`, etc.) como proveedores remotos (**OpenRouter**, **OpenAI**).

---

## Requisitos

- Python 3.10 o superior
- Ollama (opcional, para ejecución 100% local) o clave de API de OpenAI / OpenRouter

---

## Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/vicentecuritol/spectre.git
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

## Modos de Uso

### 1. Modo Directo (Single-Shot)
Pasa tu orden directamente como argumento. Ideal para scripts o alias rápidos de terminal:
```bash
python main.py "escanear puertos 80 y 443 con nmap"
# Salida: nmap -p 80,443 <objetivo>
# [Copiado al portapapeles]
```

### 2. Modo Interactivo (Sesión de terminal)
Inicia la consola interactiva:
```bash
python main.py
```

#### Comandos Internos
- `:why` / `:explain` - Explica la sintaxis y flags del último comando generado.
- `:exec` / `:run` - Ejecuta el comando en tu terminal previa confirmación `[y/N]`.
- `:models` - Lista los modelos instalados en tu Ollama local.
- `:model <nombre>` - Cambia el modelo activo en caliente (ej: `:model llama3:8b`).
- `:status` - Muestra el modelo activo, endpoint y estadísticas de notas indexadas.
- `:reload` - Fuerza la reindexación de los archivos en `payloads/`.
- `:clear` - Limpia la pantalla de la terminal.
- `:help` - Muestra la lista de comandos.
- `:exit` - Cierra Spectre (o `Ctrl+C`).

---

## Base de Conocimiento Local (`payloads/`)

Puedes añadir cualquier archivo `.txt` o `.md` dentro de la carpeta `payloads/` (por ejemplo guías de comandos, rangos de IP, credenciales de laboratorio o cheatsheets). 
Spectre segmenta estos archivos y realiza búsquedas semánticas por relevancia. Si tu consulta no guarda relación con los archivos, no inyecta nada para mantener la inferencia en su máxima velocidad.

---

## Estructura del Proyecto

```
spectre/
├── .env.example        # Plantilla de variables de entorno
├── .gitignore          # Reglas de exclusión de git
├── ai_engine.py        # Motor de conexión, inferencia y explicación
├── file_reader.py      # Micro-RAG: indexador, segmentador y buscador selectivo
├── main.py             # Interfaz CLI (modo directo e interactivo)
├── payloads/           # Base de conocimiento local (.txt, .md)
│   ├── apuntes_redes.txt
│   └── guia_nmap.txt
├── README.md           # Documentación del proyecto
├── requirements.txt    # Dependencias de Python
└── utils.py            # Utilidades de portapapeles y ejecución de sistema
```
