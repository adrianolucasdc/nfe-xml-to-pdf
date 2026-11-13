"""Domain ports (interfaces) for nfe2pdf - Strategy Pattern."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from nfe2pdf.domain.models import NFeData


@dataclass(frozen=True)
class PDFGeneratorConfig:
    """Configuration for PDF generation (independent of BrazilFiscalReport)."""
    layout: str = "auto"                    # auto | nt_2026_010 | moc_7_0
    logo_path: str | None = None
    margins_mm: tuple[float, float, float, float] = (5, 5, 5, 5)  # top, right, bottom, left
    font_type: str = "times"                # times | courier
    font_size: str = "small"                # small | big
    tax_configuration: str = "standard_icms_ipi"
    invoice_display: str = "full_details"
    display_pis_cofins: bool = False
    watermark_cancelled: bool = True
    infcpl_semicolon_newline: bool = False
    receipt_position: str = "top"           # top | bottom | left
    carrier_receipt: bool = False
    # Footer stamp
    footer_text: str = ""
    footer_logo: str | None = None
    footer_height: float = 5
    footer_logo_max_width: float = 20
    footer_spacing: float = 1


class XMLParser(Protocol):
    """Port for parsing NF-e XML files."""

    def parse(self, xml_content: bytes) -> NFeData:
        """Parse XML bytes and return structured NFeData.

        Args:
            xml_content: Raw XML content as bytes.

        Returns:
            NFeData: Parsed and validated NF-e data.

        Raises:
            InvalidXmlError: If XML is malformed.
            NotNFeError: If XML is not an NF-e (wrong namespace).
            InvalidNFeVersionError: If NF-e version is not supported.
        """
        ...

    def parse_file(self, xml_path: Path) -> NFeData:
        """Parse XML file and return structured NFeData.

        Args:
            xml_path: Path to XML file.

        Returns:
            NFeData: Parsed and validated NF-e data.
        """
        ...


class PDFGenerator(Protocol):
    """Port for generating DANFE PDF from NF-e data."""

    def generate(self, nfe_data: NFeData, config: PDFGeneratorConfig) -> bytes:
        """Generate DANFE PDF bytes from NF-e data.

        Args:
            nfe_data: Parsed NF-e data.
            config: PDF generation configuration.

        Returns:
            bytes: PDF content.

        Raises:
            PDFGenerationError: If PDF generation fails.
        """
        ...


class FileAssociationManager(Protocol):
    """Port for managing Windows file associations."""

    def is_associated(self, extension: str = ".xml") -> bool:
        """Check if extension is associated with this application."""
        ...

    def associate(self, extension: str = ".xml", description: str = "NF-e XML Document") -> None:
        """Associate extension with this application."""
        ...

    def unassociate(self, extension: str = ".xml") -> None:
        """Remove association for extension."""
        ...


class ConfigManager(Protocol):
    """Port for managing application configuration."""

    def load(self) -> dict:
        """Load configuration from file."""
        ...

    def save(self, config: dict) -> None:
        """Save configuration to file."""
        ...

    def get_default_config(self) -> dict:
        """Get default configuration."""
        ...