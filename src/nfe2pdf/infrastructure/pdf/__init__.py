"""PDF infrastructure package for nfe2pdf."""

from __future__ import annotations

from nfe2pdf.infrastructure.pdf.base import PDFGeneratorBase
from nfe2pdf.infrastructure.pdf.bfr_adapter import BFRAdapter, create_pdf_generator

__all__ = [
    "BFRAdapter",
    "create_pdf_generator",
    "PDFGeneratorBase",
]
