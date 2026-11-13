"""BFR Adapter - implements PDFGenerator port using BrazilFiscalReport."""
from __future__ import annotations

from nfe2pdf.domain.models import NFeData
from nfe2pdf.domain.ports import PDFGenerator, PDFGeneratorConfig
from nfe2pdf.domain.exceptions import PDFGenerationError


class BFRAdapter:
    """Adapter for BrazilFiscalReport Danfe generator.

    Implements the PDFGenerator port to isolate the LGPL dependency
    behind our own interface. This allows swapping the PDF engine
    (e.g., to reportlab/weasyprint) without touching domain code.
    """

    def __init__(self) -> None:
        self._danfe_class = None
        self._danfe_config_class = None
        self._layout_enum = None
        self._init_bfr()

    def _init_bfr(self) -> None:
        """Lazy import of BrazilFiscalReport to avoid hard dependency at import time."""
        try:
            from brazilfiscalreport.danfe import Danfe
            from brazilfiscalreport.danfe.config import DanfeConfig, DanfeLayout
            self._danfe_class = Danfe
            self._danfe_config_class = DanfeConfig
            self._layout_enum = DanfeLayout
        except ImportError as e:
            raise PDFGenerationError(
                "BrazilFiscalReport não está instalado. Instale com: pip install brazilfiscalreport",
                original_error=e,
            )

    def _map_layout(self, layout: str):
        """Map our layout string to BFR DanfeLayout enum."""
        layout_map = {
            "auto": self._layout_enum.AUTO,
            "nt_2026_010": self._layout_enum.NT_2026_010,
            "moc_7_0": self._layout_enum.MOC_7_0,
        }
        return layout_map.get(layout, self._layout_enum.AUTO)

    def _map_font_type(self, font_type: str):
        """Map font type to BFR FontType enum."""
        from brazilfiscalreport.danfe.config import FontType
        return FontType.TIMES if font_type.lower() == "times" else FontType.COURIER

    def _map_font_size(self, font_size: str):
        """Map font size to BFR FontSize enum."""
        from brazilfiscalreport.danfe.config import FontSize
        return FontSize.BIG if font_size.lower() == "big" else FontSize.SMALL

    def _map_tax_config(self, tax_config: str):
        """Map tax configuration to BFR TaxConfiguration enum."""
        from brazilfiscalreport.danfe.config import TaxConfiguration
        mapping = {
            "standard_icms_ipi": TaxConfiguration.STANDARD_ICMS_IPI,
            "icms_st": TaxConfiguration.ICMS_ST,
            "without_ipi": TaxConfiguration.WITHOUT_IPI,
        }
        return mapping.get(tax_config, TaxConfiguration.STANDARD_ICMS_IPI)

    def _map_invoice_display(self, display: str):
        """Map invoice display to BFR InvoiceDisplay enum."""
        from brazilfiscalreport.danfe.config import InvoiceDisplay
        return InvoiceDisplay.FULL_DETAILS if display == "full_details" else InvoiceDisplay.DUPLICATES_ONLY

    def _map_receipt_position(self, position: str):
        """Map receipt position to BFR ReceiptPosition enum."""
        from brazilfiscalreport.danfe.config import ReceiptPosition
        mapping = {
            "top": ReceiptPosition.TOP,
            "bottom": ReceiptPosition.BOTTOM,
            "left": ReceiptPosition.LEFT,
        }
        return mapping.get(position, ReceiptPosition.TOP)

    def _build_bfr_config(self, config: PDFGeneratorConfig):
        """Convert our PDFGeneratorConfig to BFR DanfeConfig."""
        from brazilfiscalreport.danfe.config import (
            DanfeConfig,
            Margins,
            DecimalConfig,
            ProductDescriptionConfig,
            FooterStamp,
        )

        # Logo handling - BFR accepts path string, BytesIO, or bytes
        logo = config.logo_path

        bfr_config = DanfeConfig(
            logo=logo,
            margins=Margins(
                top=config.margins_mm[0],
                right=config.margins_mm[1],
                bottom=config.margins_mm[2],
                left=config.margins_mm[3],
            ),
            receipt_pos=self._map_receipt_position(config.receipt_position),
            carrier_receipt=config.carrier_receipt,
            decimal_config=DecimalConfig(
                price_precision=4,
                quantity_precision=4,
            ),
            tax_configuration=self._map_tax_config(config.tax_configuration),
            invoice_display=self._map_invoice_display(config.invoice_display),
            font_type=self._map_font_type(config.font_type),
            font_size=self._map_font_size(config.font_size),
            display_pis_cofins=config.display_pis_cofins,
            watermark_cancelled=config.watermark_cancelled,
            infcpl_semicolon_newline=config.infcpl_semicolon_newline,
            product_description_config=ProductDescriptionConfig(
                display_branch=False,
                display_anp=False,
                display_anvisa=False,
                display_additional_info=True,
                display_xped=False,
                branch_info_prefix="",
            ),
            footer_stamp=FooterStamp(
                logo=config.footer_logo,
                text=config.footer_text,
                height=config.footer_height,
                logo_max_width=config.footer_logo_max_width,
                spacing=config.footer_spacing,
            ),
            layout=self._map_layout(config.layout),
        )
        return bfr_config

    def generate(self, nfe_data: NFeData, config: PDFGeneratorConfig) -> bytes:
        """Generate DANFE PDF bytes from NF-e data.

        Args:
            nfe_data: Parsed NF-e data (our domain model).
            config: PDF generation configuration.

        Returns:
            bytes: PDF content.

        Raises:
            PDFGenerationError: If PDF generation fails.
        """
        if self._danfe_class is None:
            self._init_bfr()

        try:
            # BFR expects raw XML bytes, not our domain model.
            # We need to reconstruct XML from NFeData or use original XML.
            # For now, we require the original XML to be passed via a special attribute.
            # This is a design decision: BFR works from XML, not from parsed objects.

            # Check if nfe_data has original XML attached (set by use case)
            xml_bytes = getattr(nfe_data, "_original_xml", None)
            if xml_bytes is None:
                raise PDFGenerationError(
                    "XML original não disponível para geração do PDF. "
                    "O use case deve anexar o XML bruto em nfe_data._original_xml"
                )

            # Build BFR config
            bfr_config = self._build_bfr_config(config)

            # Generate PDF using BFR
            danfe = self._danfe_class(xml=xml_bytes, config=bfr_config)
            pdf_bytes = danfe.output()

            if not pdf_bytes:
                raise PDFGenerationError("BrazilFiscalReport retornou PDF vazio")

            return pdf_bytes

        except PDFGenerationError:
            raise
        except Exception as e:
            raise PDFGenerationError(
                f"Erro ao gerar PDF com BrazilFiscalReport: {e}",
                original_error=e,
            )


# Factory function for dependency injection
def create_pdf_generator() -> PDFGenerator:
    """Create a PDFGenerator instance (BFRAdapter)."""
    return BFRAdapter()