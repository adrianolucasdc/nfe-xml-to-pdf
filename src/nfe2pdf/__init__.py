"""nfe2pdf - Conversor NF-e XML para PDF (DANFE)."""
from __future__ import annotations

from nfe2pdf.config import Settings, get_settings, reload_settings

__version__ = "0.1.0"
__author__ = "Adriano Lucas"
__license__ = "MIT"

__all__ = [
    "Settings",
    "get_settings",
    "reload_settings",
]