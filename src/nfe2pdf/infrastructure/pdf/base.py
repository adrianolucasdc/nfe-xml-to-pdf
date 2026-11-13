"""Base PDF Generator abstract class (optional - Protocol is primary)."""
from __future__ import annotations

from abc import ABC, abstractmethod

from nfe2pdf.domain.models import NFeData
from nfe2pdf.domain.ports import PDFGeneratorConfig


class PDFGeneratorBase(ABC):
    """Abstract base class for PDF generators.

    Note: The primary contract is the `PDFGenerator` Protocol in domain.ports.
    This ABC exists for shared implementation logic if needed.
    """

    @abstractmethod
    def generate(self, nfe_data: NFeData, config: PDFGeneratorConfig) -> bytes:
        """Generate DANFE PDF from NF-e data."""
        ...