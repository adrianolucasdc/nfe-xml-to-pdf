"""Windows infrastructure package for nfe2pdf."""
from __future__ import annotations

from nfe2pdf.infrastructure.windows.registry import WindowsRegistryManager, is_windows

__all__ = [
    "WindowsRegistryManager",
    "is_windows",
]