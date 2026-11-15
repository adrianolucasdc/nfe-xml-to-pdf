"""Infrastructure package for nfe2pdf."""

from __future__ import annotations

from nfe2pdf.infrastructure.config_manager import PydanticConfigManager, create_config_manager
from nfe2pdf.infrastructure.pdf import BFRAdapter, PDFGeneratorBase, create_pdf_generator
from nfe2pdf.infrastructure.windows import WindowsRegistryManager, is_windows
from nfe2pdf.infrastructure.xml import NFexmlParser, NFexmlValidator

__all__ = [
    "NFexmlParser",
    "NFexmlValidator",
    "BFRAdapter",
    "create_pdf_generator",
    "PDFGeneratorBase",
    "PydanticConfigManager",
    "create_config_manager",
    "WindowsRegistryManager",
    "is_windows",
]
