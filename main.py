import os
import sys
from ai_engine import ask_model, get_engine_info
from file_reader import get_relevant_context, reload_payloads, get_payload_stats


def print_banner():
    info = get_engine_info()
    stats = get_payload_stats()
    
    print("=" * 60)
    print("  SPECTRE CLI - Asistente de Sintaxis & Comandos")
    print(f"  Modelo:   {info['model']}")
    print(f"  Endpoint: {info['base_url']}")
    print(f"  Payloads: {stats['files_count']} archivo(s) | {stats['chunks_count']} fragmentos indexados")
    print("  Escribe tu orden o usa :help para ver comandos internos.")
    print("=" * 60)


def print_help():
    print("\n--- Comandos Internos de Spectre ---")
    print("  :status   Muestra estado del modelo y estadísticas de notas")
    print("  :reload   Fuerza reindexación de los archivos en 'payloads/'")
    print("  :clear    Limpia la pantalla de la terminal")
    print("  :help     Muestra esta ayuda")
    print("  :exit     Sale de la aplicación (o Ctrl+C)\n")


def main():
    print_banner()

    while True:
        try:
            prompt = input("\n> ").strip()
            if not prompt:
                continue

            # Comandos internos
            if prompt in (":exit", ":quit", "exit", "quit"):
                print("\nSaliendo de Spectre...")
                break
            elif prompt in (":help", ":?"):
                print_help()
                continue
            elif prompt in (":clear", ":cls"):
                os.system("cls" if os.name == "nt" else "clear")
                print_banner()
                continue
            elif prompt == ":reload":
                reload_payloads(force=True)
                stats = get_payload_stats()
                print(f"[✓] Base de payloads recargada: {stats['files_count']} archivo(s), {stats['chunks_count']} fragmentos.")
                continue
            elif prompt == ":status":
                info = get_engine_info()
                stats = get_payload_stats()
                print(f"\n[Estado] Modelo: {info['model']}")
                print(f"[Estado] Endpoint: {info['base_url']}")
                print(f"[Estado] Modo Local: {'Sí' if info['is_local'] else 'No'}")
                print(f"[Estado] Archivos en payloads: {stats['files_count']} ({stats['chunks_count']} fragmentos indexados)\n")
                continue

            # Búsqueda selectiva de contexto (Micro-RAG en memoria)
            context, sources = get_relevant_context(prompt)
            if sources:
                sources_str = ", ".join(sources)
                print(f"\033[90m[Ref: {sources_str}]\033[0m")

            # Inferencia con streaming
            response = ask_model(prompt, context)
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    print(content, end="", flush=True)
            print()

        except KeyboardInterrupt:
            # Si el usuario presiona Ctrl+C durante la generación, no tumba el script
            print("\n[Operación cancelada por el usuario]")
        except EOFError:
            print("\nSaliendo de Spectre...")
            break
        except Exception as e:
            print(f"\n[!] Error: {e}")


if __name__ == "__main__":
    main()