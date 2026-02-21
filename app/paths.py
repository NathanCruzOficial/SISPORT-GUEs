from __future__ import annotations

import os
from pathlib import Path

APP_DIR_NAME = "SISPORT"


def get_local_appdata_dir() -> Path:
    """
    Retorna a pasta base do app em %LOCALAPPDATA%\SISPORT
    """
    base = os.environ.get("LOCALAPPDATA")
    if not base:
        # fallback raro (ambientes diferentes)
        base = str(Path.home() / "AppData" / "Local")
    return Path(base) / APP_DIR_NAME


def ensure_app_dirs() -> dict[str, Path]:
    """
    Garante que as pastas existam e retorna os caminhos.
    """
    root = get_local_appdata_dir()
    db_dir = root / "db"
    uploads_dir = root / "uploads"
    logs_dir = root / "logs"

    db_dir.mkdir(parents=True, exist_ok=True)
    uploads_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    return {
        "root": root,
        "db_dir": db_dir,
        "uploads_dir": uploads_dir,
        "logs_dir": logs_dir,
    }


def get_db_path(filename: str = "data.sqlite3") -> Path:
    dirs = ensure_app_dirs()
    return dirs["db_dir"] / filename
