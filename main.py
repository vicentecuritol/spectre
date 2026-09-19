import os
import sys

# Asegurar codificación UTF-8 en terminales de Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

from ai_engine import (
    ask_model,
    explain_command,
    set_model,
    list_available_models,
    get_engine_info,
)
from file_reader import get_relevant_context, reload_payloads, get_payload_stats
from utils import copy_to_clipboard, execute_command_interactive


def print_banner():
    info = get_engine_info()
    stats = get_payload_stats()
    
    print("\033[1;36m=" * 62 + "\033[0m")
    print("  \033[1;37mSPECTRE CLI ⚡ - Asistente de Sintaxis & Comandos\033[0m")
    print(f"  \033[90mModelo:\033[0m   \033[33m{info['model']}\033[0m")
    print(f"  \033[90mEndpoint:\033[0m {info['base_url']}")
    print(f"  \033[90mPayloads:\033[0m {stats['files_count']} archivo(s) | {stats['chunks_count']} fragmentos indexados")
    print("  \033[90mEscribe tu orden, :help para ayuda o :exit para salir.\033[0m")
    print("\033[1;36m=" * 62 + "\033[0m")


def print_help():
    print("\n\033[1;37m--- Comandos Internos de Spectre ---\033[0m")
    print("  \033[1;32m:why\033[0m / \033[1;32m:explain\033[0m Explica los flags y sintaxis del último comando generado")
    print("  \033[1;32m:exec\033[0m / \033[1;32m:run\033[0m    Ejecuta el último comando en tu terminal (con confirmación)")
    print("  \033[1;32m:models\033[0m           Lista los modelos descargados en tu Ollama local")
    print("  \033[1;32m:model <nombre>\033[0m   Cambia el modelo de IA activo en caliente")
    print("  \033[1;32m:status\033[0m           Muestra información del modelo y estadísticas de notas")
    print("  \033[1;32m:reload\033[0m           Fuerza la reindexación de los archivos en 'payloads/'")
    print("  \033[1;32m:clear\033[0m            Limpia la pantalla de la terminal")
    print("  \033[1;32m:help\033[0m             Muestra esta lista de comandos")
    print("  \033[1;32m:exit\033[0m             Cierra Spectre (o usa Ctrl+C)\n")


def execute_query(prompt: str, auto_copy: bool = True) -> str:
    """Procesa una consulta, muestra referencias y transmite la respuesta."""
    context, sources = get_relevant_context(prompt)
    if sources:
        sources_str = ", ".join(sources)
        print(f"\033[90m[Ref: {sources_str}]\033[0m")

    response = ask_model(prompt, context)
    generated = []
    
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)
            generated.append(content)
    print()

    full_output = "".join(generated).strip()

    if auto_copy and full_output:
        if copy_to_clipboard(full_output):
            print("\033[90m[Copiado al portapapeles]\033[0m")

    return full_output


def run_interactive():
    """Modo interactivo (bucle de terminal)."""
    print_banner()
    last_command = ""

    while True:
        try:
            prompt = input("\n\033[1;36m>\033[0m ").strip()
            if not prompt:
                continue

            # Comandos de salida
            if prompt in (":exit", ":quit", "exit", "quit"):
                print("\n\033[90mSaliendo de Spectre...\033[0m")
                break

            # Ayuda
            elif prompt in (":help", ":?"):
                print_help()
                continue

            # Limpieza de pantalla
            elif prompt in (":clear", ":cls"):
                os.system("cls" if os.name == "nt" else "clear")
                print_banner()
                continue

            # Recarga de payloads
            elif prompt == ":reload":
                reload_payloads(force=True)
                stats = get_payload_stats()
                print(f"\033[32m[✓] Base de payloads recargada: {stats['files_count']} archivo(s), {stats['chunks_count']} fragmentos.\033[0m")
                continue

            # Estado
            elif prompt == ":status":
                info = get_engine_info()
                stats = get_payload_stats()
                print(f"\n\033[90m[Estado]\033[0m Modelo: \033[33m{info['model']}\033[0m")
                print(f"\033[90m[Estado]\033[0m Endpoint: {info['base_url']}")
                print(f"\033[90m[Estado]\033[0m Modo Local: {'Sí' if info['is_local'] else 'No'}")
                print(f"\033[90m[Estado]\033[0m Archivos en payloads: {stats['files_count']} ({stats['chunks_count']} fragmentos indexados)\n")
                continue

            # Listar modelos en Ollama
            elif prompt == ":models":
                models = list_available_models()
                if models:
                    print("\n\033[1;37mModelos disponibles en Ollama local:\033[0m")
                    for m in models:
                        prefix = "->" if m == get_engine_info()["model"] else "  "
                        print(f"  {prefix} \033[33m{m}\033[0m")
                    print("\nUsa :model <nombre> para cambiar de modelo.")
                else:
                    print("\033[93m[!] No se pudieron listar modelos de Ollama o no estás en modo local.\033[0m")
                continue

            # Cambiar modelo activo
            elif prompt.startswith(":model "):
                new_m = prompt.replace(":model ", "").strip()
                if new_m:
                    set_model(new_m)
                    print(f"\033[32m[✓] Modelo activo cambiado a: {new_m}\033[0m")
                continue

            # Explicación del último comando
            elif prompt in (":why", ":explain") or prompt.startswith("?"):
                if prompt in (":why", ":explain"):
                    cmd_to_explain = last_command
                else:
                    cmd_to_explain = prompt.lstrip("?").strip() or last_command

                if not cmd_to_explain:
                    print("\033[93m[!] No hay ningún comando previo para explicar.\033[0m")
                    continue
                print(f"\n\033[90mExplicando:\033[0m \033[32m{cmd_to_explain}\033[0m\n")
                res = explain_command(cmd_to_explain)
                for chunk in res:
                    c = chunk.choices[0].delta.content
                    if c:
                        print(c, end="", flush=True)
                print()
                continue

            # Ejecutar último comando de forma segura
            elif prompt in (":exec", ":run"):
                if not last_command:
                    print("\033[93m[!] No hay ningún comando previo para ejecutar.\033[0m")
                    continue
                execute_command_interactive(last_command)
                continue

            # Consulta normal
            output = execute_query(prompt, auto_copy=True)
            if output:
                last_command = output

        except KeyboardInterrupt:
            print("\n\033[90m[Operación cancelada por el usuario]\033[0m")
        except EOFError:
            print("\n\033[90mSaliendo de Spectre...\033[0m")
            break
        except Exception as e:
            print(f"\n\033[91m[!] Error: {e}\033[0m")


def main():
    # Soporte para ejecución directa con argumentos (modo single-shot)
    # Ejemplo: python main.py "escanear puertos 80 y 443 con nmap"
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:]).strip()
        if query in ("-h", "--help", "help"):
            print("Uso: python main.py [consulta]")
            print("     python main.py           (inicia sesión interactiva)")
            sys.exit(0)
        try:
            execute_query(query, auto_copy=True)
        except Exception as e:
            print(f"\033[91m[!] Error: {e}\033[0m")
            sys.exit(1)
        sys.exit(0)

    # Modo interactivo por defecto
    run_interactive()


if __name__ == "__main__":
    main()