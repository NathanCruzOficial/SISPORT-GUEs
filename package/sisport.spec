# -*- mode: python ; coding: utf-8 -*-

datas = [
    ("app/templates", "app/templates"),
    ("app/static", "app/static"),
]

a = Analysis(
    ["desktop_app.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.datas,
    name="SISPORT",
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="SISPORT",
)
