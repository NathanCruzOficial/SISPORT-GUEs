# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

spec_dir = os.path.dirname(os.path.abspath(SPEC))
project_root = os.path.abspath(os.path.join(spec_dir, ".."))

datas = [
    (os.path.join(project_root, "app", "templates"), os.path.join("app", "templates")),
    (os.path.join(project_root, "app", "static"), os.path.join("app", "static")),
]

a = Analysis(
    [os.path.join(project_root, "desktop_app.py")],
    pathex=[project_root, os.path.join(project_root, "app")],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    [],                  # <- NÃO coloque a.datas aqui
    name="SISPORT",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,           # <- desliga UPX pra eliminar variável
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=False,       # <- chave
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name="SISPORT",
)
