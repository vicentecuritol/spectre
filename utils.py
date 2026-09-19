import os
import sys
import platform
import subprocess
from typing import Optional


def copy_to_clipboard(text: str) -> bool:
    """
    Copia texto al portapapeles del sistema operativo sin dependencias externas.
    Soporta Windows (clip), macOS (pbcopy) y Linux (xclip / wl-copy).
    """
    cleaned = text.strip()
    if not cleaned:
        return False

    os_type = platform.system()
    try:
        if os_type == "Windows":
            # clip en Windows espera codificación utf-8 o oem
            p = subprocess.Popen(["clip"], stdin=subprocess.PIPE, shell=True)
            p.communicate(input=cleaned.encode("utf-8"))
            return p.returncode == 0
        elif os_type == "Darwin":
            p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
            p.communicate(input=cleaned.encode("utf-8"))
            return p.returncode == 0
        elif os_type == "Linux":
            # Intentar wl-copy (Wayland) o xclip (X11)
            try:
                p = subprocess.Popen(["wl-copy"], stdin=subprocess.PIPE)
                p.communicate(input=cleaned.encode("utf-8"))
                return p.returncode == 0
            except FileNotFoundError:
                p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
                p.communicate(input=cleaned.encode("utf-8"))
                return p.returncode == 0
    except Exception:
        return False
    return False


def execute_command_interactive(command: str) -> None:
    """
    Ejecuta un comando en la shell del sistema previa confirmación explícita del usuario.
    """
    cmd = command.strip()
    if not cmd:
        print("\033[93m[!] No hay ningún comando para ejecutar.\033[0m")
        return

    print(f"\n\033[93m¿Deseas ejecutar este comando en tu terminal?\033[0m")
    print(f"\033[1;32m$ {cmd}\033[0m")
    
    try:
        confirm = input("\033[93mConfirmar ejecución [y/N]: \033[0m").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\n[Operación cancelada]")
        return

    if confirm in ("y", "yes", "s", "si", "sí"):
        print("\n\033[90m--- Salida del comando ---\033[0m")
        try:
            # En Windows ejecuta vía powershell / cmd; en Unix vía sh
            is_win = platform.system() == "Windows"
            subprocess.run(cmd, shell=True, check=False)
        except Exception as e:
            print(f"\033[91m[!] Error al ejecutar: {e}\033[0m")
        print("\033[90m---------------------------\033[0m")
    else:
        print("[!] Ejecución descartada.")
