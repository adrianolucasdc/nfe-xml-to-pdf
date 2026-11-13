"""Infrastructure package for nfe2pdf."""
from __future__ import annotations

from nfe2pdf.infrastructure.xml import NFexmlParser, NFexmlValidator
from nfe2pdf.infrastructure.pdf import BFRAdapter, create_pdf_generator, PDFGeneratorBase
from nfe2pdf.infrastructure.config_manager import PydanticConfigManager, create_config_manager

__all__ = [
    "NFexmlParser",
    "NFexmlValidator",
    "BFRAdapter",
    "create_pdf_generator",
    "PDFGeneratorBase",
    "PydanticConfigManager",
    "create_config_manager",
]