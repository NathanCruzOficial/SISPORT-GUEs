"""
test_updater.py
Teste completo do updater — mostra log detalhado no terminal
e abre o diálogo Tkinter normalmente.
"""

import os
import sys
import tempfile
import subprocess

import requests
from packaging import version

import tkinter as tk
from tkinter import messagebox

from version import __version__, APP_NAME, GITHUB_REPO

# ── Simula versão antiga para forçar a detecção de update ──
FAKE_OLD_VERSION = "0.0.1"


def test_full_update():
    current = FAKE_OLD_VERSION

    print("=" * 55)
    print(f"  🧪 TESTE DO UPDATER — {APP_NAME}")
    print("=" * 55)
    print(f"  Repo:            {GITHUB_REPO}")
    print(f"  Versão real:     {__version__}")
    print(f"  Versão simulada: {current}")
    print("=" * 55)

    # ── 1. Consultar GitHub ──
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    print(f"\n🔍 Consultando GitHub...")
    print(f"   GET {url}")

    try:
        r = requests.get(url, timeout=10)
        print(f"   Status: {r.status_code}")
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
        return

    if r.status_code == 404:
        print("   ❌ Nenhuma release encontrada no repositório.")
        return

    r.raise_for_status()
    rel = r.json()

    # ── 2. Versão remota ──
    tag = rel.get("tag_name", "???")
    latest = tag.lstrip("v").strip()
    print(f"\n📦 Release mais recente:")
    print(f"   Tag:    {tag}")
    print(f"   Versão: {latest}")
    print(f"   Nome:   {rel.get('name', '—')}")
    print(f"   Data:   {rel.get('published_at', '—')}")

    # ── 3. Comparação ──
    local_v = version.parse(current)
    remote_v = version.parse(latest)
    print(f"\n⚖️  Comparação:")
    print(f"   Local (simulada): {local_v}")
    print(f"   Remota:           {remote_v}")

    if remote_v <= local_v:
        print("   ⏸️  Já está na versão mais recente. Nada a fazer.")
        return

    print("   ✅ ATUALIZAÇÃO DISPONÍVEL!")

    # ── 4. Diálogo Tkinter ──
    msg = (
        f"Existe uma nova versão do {APP_NAME}.\n\n"
        f"Instalada: {current}\n"
        f"Disponível: {latest}\n\n"
        "Deseja atualizar agora?"
    )

    print(f"\n💬 Abrindo diálogo Tkinter...")
    root = tk.Tk()
    root.withdraw()
    accepted = messagebox.askyesno("Atualização disponível", msg)

    if not accepted:
        print("   ❌ Usuário recusou a atualização.")
        return

    print("   ✅ Usuário aceitou a atualização!")

    # ── 5. Localizar asset ──
    assets = rel.get("assets", [])
    print(f"\n📎 Assets da release ({len(assets)}):")

    installer_asset = None
    for a in assets:
        name = a.get("name", "???")
        size_mb = a.get("size", 0) / (1024 * 1024)
        is_installer = name.lower().endswith("_setup.exe")
        marker = " ← INSTALADOR" if is_installer else ""
        print(f"   • {name} ({size_mb:.1f} MB){marker}")

        if is_installer:
            installer_asset = a

    if not installer_asset:
        print("\n   ❌ Nenhum asset terminando em '_setup.exe' encontrado!")
        return

    # ── 6. Download ──
    download_url = installer_asset["browser_download_url"]
    print(f"\n⬇️  Baixando instalador...")
    print(f"   URL: {download_url}")

    fd, installer_path = tempfile.mkstemp(suffix=".exe")
    os.close(fd)

    with requests.get(download_url, stream=True, timeout=120) as resp:
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0))
        downloaded = 0

        with open(installer_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 256):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = downloaded / total * 100
                        print(f"   ⏳ {pct:5.1f}%  ({downloaded / 1024 / 1024:.1f} MB)", end="\r")

    print(f"\n   ✅ Download concluído!")
    print(f"   Salvo em: {installer_path}")
    print(f"   Tamanho:  {os.path.getsize(installer_path) / 1024 / 1024:.1f} MB")

    # ── 7. Executar instalador ──
    print(f"\n🚀 Executando instalador...")
    subprocess.Popen([installer_path], shell=False)
    print("   ✅ Instalador iniciado. Encerrando aplicação.")
    sys.exit(0)


if __name__ == "__main__":
    test_full_update()
