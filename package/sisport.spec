# -*- mode: python ; coding: utf-8 -*-

import os

# SPECPATH = diretório onde o .spec está (package/)
base_dir = os.path.abspath(os.path.join(SPECPATH, '..'))

datas = [
    (os.path.join(base_dir, 'icone.ico'), '.'),
    (os.path.join(base_dir, 'app', 'templates'), 'app/templates'),
    (os.path.join(base_dir, 'app', 'static'), 'app/static'),
]

a = Analysis(
    [os.path.join(base_dir, 'main.py')],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    icon=os.path.join(base_dir, 'icone.ico'),
    name='sisport',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='sisport',
)
