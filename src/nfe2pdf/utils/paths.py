"""Path resolution for nfe2pdf."""
from __future__ import annotations

import os
import sys
from pathlib import Path


def get_app_dir() -> Path:
    """Diretório da aplicação instalada (Program Files\\nfe2pdf ou dev root)."""
    if getattr(sys, "frozen", False):
        # PyInstaller: sys._MEIPASS é o temp dir, sys.executable é o .exe
        return Path(sys.executable).parent
    # Desenvolvimento: src/nfe2pdf/utils/paths.py -> project root
    return Path(__file__).resolve().parent.parent.parent.parent


def get_config_dir() -> Path:
    """Diretório de configuração no AppData: %APPDATA%\\nfe2pdf"""
    appdata = os.getenv("APPDATA")
    if not appdata:
        # Fallback para Linux/Mac (não suportado oficialmente, mas evita crash)
        appdata = str(Path.home() / ".config")
    return Path(appdata) / "nfe2pdf"


def get_config_path() -> Path:
    """Caminho completo do config.yaml."""
    return get_config_dir() / "config.yaml"


def get_logo_path() -> Path | None:
    """Caminho da logo padrão do pacote (assets/logo.png)."""
    # Em produção (PyInstaller --add-data), a logo vai para _MEIPASS/assets/logo.png
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        logo = base / "assets" / "logo.png"
        if logo.exists():
            return logo
    # Desenvolvimento
    dev_logo = get_app_dir() / "assets" / "logo.png"
    if dev_logo.exists():
        return dev_logo
    return None


def ensure_config_dir() -> Path:
    """Cria o diretório de config se não existir."""
    cfg_dir = get_config_dir()
    cfg_dir.mkdir(parents=True, exist_ok=True)
    return cfg_dir


def get_default_output_dir() -> Path | None:
    """Retorna None para usar a mesma pasta do XML (configurável)."""
    return None