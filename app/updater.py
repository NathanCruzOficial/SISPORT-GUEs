import os
import sys
import tempfile
import subprocess

import requests
from packaging import version

import tkinter as tk
from tkinter import messagebox


def _ask_yes_no(title: str, message: str) -> bool:
    root = tk.Tk()
    root.withdraw()
    return messagebox.askyesno(title, message)


def _get_latest_release(repo: str) -> dict:
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()


def _pick_installer_asset(release_json: dict) -> dict:
    """
    Padronize o nome do asset do instalador, ex:
      SISPORTSetup.exe
    e/ou qualquer coisa terminando com Setup.exe
    """
    for a in release_json.get("assets", []):
        name = (a.get("name") or "").lower()
        if name.endswith("_setup.exe"):
            return a
    raise RuntimeError("Release encontrada, mas não achei nenhum asset terminando em 'Setup.exe'.")


def _download_to_temp(url: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".exe")
    os.close(fd)

    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 256):
                if chunk:
                    f.write(chunk)
    return path


def check_and_offer_update(current_version: str, repo: str, app_name: str) -> None:
    """
    Rode isso no início do programa.
    Se o usuário aceitar, executa o instalador e encerra o app.
    """
    try:
        rel = _get_latest_release(repo)
        latest = (rel.get("tag_name") or "").lstrip("v").strip()
        if not latest:
            return

        if version.parse(latest) <= version.parse(current_version):
            return

        msg = (
            f"Existe uma nova versão do {app_name}.\n\n"
            f"Instalada: {current_version}\n"
            f"Disponível: {latest}\n\n"
            "Deseja atualizar agora?"
        )

        if not _ask_yes_no("Atualização disponível", msg):
            return

        asset = _pick_installer_asset(rel)
        installer_url = asset["browser_download_url"]
        installer_path = _download_to_temp(installer_url)

        # Executa o instalador em modo normal (vai perguntar pasta, permissões, etc.)
        subprocess.Popen([installer_path], shell=False)
        sys.exit(0)

    except Exception:
        # Em produção: logar isso em arquivo. Não travar o app por causa do update.
        return
