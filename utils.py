import os
import re
import sys
import shutil
import platform
import subprocess
from typing import Optional

# Patrones precompilados de comandos potencialmente peligrosos o destructivos
DANGEROUS_PATTERNS = [
    re.compile(r"\brm\s+-(?:[a-z]*r[a-z]*f|[a-z]*f[a-z]*r)\s+/(?:\*|\s*$)", re.IGNORECASE),
    re.compile(r"\brm\s+-[a-z]+\s+-[a-z]+\s+/(?:\*|\s*$)", re.IGNORECASE),
    re.compile(r"\brm\s+.*--no-preserve-root", re.IGNORECASE),
    re.compile(r"\bmkfs\b", re.IGNORECASE),
    re.compile(r"\bdd\s+if=", re.IGNORECASE),
    re.compile(r">\s*/dev/sd[a-z]", re.IGNORECASE),
    re.compile(r"\bformat\s+[a-z]:", re.IGNORECASE),
    re.compile(r"\bdel\b.*(?:/s|/q|/f).*[a-z]:", re.IGNORECASE),
    re.compile(r"\brd\b.*(?:/s|/q).*[a-z]:", re.IGNORECASE),
    re.compile(r":\(\)\s*\{\s*:\|:&\s*\};:"),
    re.compile(r"\bchmod\s+-[a-z]*r\s+777\s+/", re.IGNORECASE),
]


def is_potentially_dangerous(command: str) -> bool:
    """Verifica si el comando contiene patrones de riesgo alto o destructivos."""
    for pattern in DANGEROUS_PATTERNS:
        if pattern.search(command):
            return True
    return False


def copy_to_clipboard(text: str) -> bool:
    """
    Copia texto al portapapeles del sistema operativo de forma segura sin dependencias externas.
    Soporta Windows (clip.exe), macOS (pbcopy) y Linux (wl-copy / xclip).
    """
    cleaned = text.strip()
    if not cleaned:
        return False

    os_type = platform.system()
    try:
        if os_type == "Windows":
            clip_path = shutil.which("clip.exe") or os.path.join(
                os.environ.get("SystemRoot", r"C:\Windows"), "System32", "clip.exe"
            )
            # shell=False previene secuestro de binarios en el directorio actual
            p = subprocess.Popen([clip_path], stdin=subprocess.PIPE, shell=False)
            p.communicate(input=cleaned.encode("utf-8"))
            return p.returncode == 0
        elif os_type == "Darwin":
            pbcopy_path = shutil.which("pbcopy")
            if not pbcopy_path:
                return False
            p = subprocess.Popen([pbcopy_path], stdin=subprocess.PIPE, shell=False)
            p.communicate(input=cleaned.encode("utf-8"))
            return p.returncode == 0
        elif os_type == "Linux":
            wl_copy = shutil.which("wl-copy")
            if wl_copy:
                p = subprocess.Popen([wl_copy], stdin=subprocess.PIPE, shell=False)
                p.communicate(input=cleaned.encode("utf-8"))
                return p.returncode == 0

            xclip = shutil.which("xclip")
            if xclip:
                p = subprocess.Popen([xclip, "-selection", "clipboard"], stdin=subprocess.PIPE, shell=False)
                p.communicate(input=cleaned.encode("utf-8"))
                return p.returncode == 0
    except Exception:
        return False
    return False


def execute_command_interactive(command: str) -> None:
    """
    Ejecuta un comando en la shell del sistema previa confirmación explícita del usuario.
    Incluye un guardián de seguridad para comandos de alto riesgo.
    """
    cmd = command.strip()
    if not cmd:
        print("\033[93m[!] No hay ningún comando para ejecutar.\033[0m")
        return

    dangerous = is_potentially_dangerous(cmd)

    if dangerous:
        print("\n\033[1;31m[PELIGRO] Se detectó un comando potencialmente destructivo.\033[0m")
        print(f"\033[1;31m$ {cmd}\033[0m")
        print("\033[91mPara autorizar esta acción riesgosa, escribe exactamente 'EJECUTAR'.\033[0m")
        try:
            confirm = input("\033[91mConfirmación estricta: \033[0m").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n[Operación cancelada]")
            return
        if confirm != "EJECUTAR":
            print("\033[93m[!] Operación abortada por seguridad.\033[0m")
            return
    else:
        print(f"\n\033[93m¿Deseas ejecutar este comando en tu terminal?\033[0m")
        print(f"\033[1;32m$ {cmd}\033[0m")
        try:
            confirm = input("\033[93mConfirmar ejecución [y/N]: \033[0m").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n[Operación cancelada]")
            return
        if confirm not in ("y", "yes", "s", "si", "sí"):
            print("[!] Ejecución descartada.")
            return

    print("\n\033[90m--- Salida del comando ---\033[0m")
    try:
        is_win = platform.system() == "Windows"
        if is_win:
            # En Windows usamos PowerShell de forma controlada
            ps = shutil.which("powershell.exe") or "powershell.exe"
            subprocess.run([ps, "-NoProfile", "-Command", cmd], shell=False, check=False)
        else:
            sh = shutil.which("bash") or shutil.which("sh") or "/bin/sh"
            subprocess.run([sh, "-c", cmd], shell=False, check=False)
    except Exception as e:
        print(f"\033[91m[!] Error al ejecutar: {e}\033[0m")
    print("\033[90m---------------------------\033[0m")
