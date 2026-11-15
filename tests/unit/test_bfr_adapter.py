"""Unit tests for BFR adapter."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from nfe2pdf.domain.exceptions import PDFGenerationError
from nfe2pdf.domain.models import (
    Address,
    Emitter,
    Header,
    NFeData,
    Recipient,
    Totals,
)
from nfe2pdf.domain.ports import PDFGeneratorConfig
from nfe2pdf.infrastructure.pdf.bfr_adapter import BFRAdapter


class TestBFRAdapter:
    """Test BFRAdapter."""

    def setup_method(self):
        self.adapter = BFRAdapter()

    def test_init_lazy_import(self):
        """Test lazy import works."""
        # Adapter initializes BFR at construction time (not lazy)
        adapter = BFRAdapter()
        assert adapter._danfe_class is not None
        assert adapter._danfe_config_class is not None
        assert adapter._layout_enum is not None

    @patch("nfe2pdf.infrastructure.pdf.bfr_adapter.BFRAdapter._init_bfr")
    def test_generate_success(self, _mock_init_bfr):
        """Test successful PDF generation."""
        # Setup mocks
        mock_danfe_class = MagicMock()
        mock_danfe_instance = MagicMock()
        mock_danfe_instance.output.return_value = b"%PDF-1.4 generated content"
        mock_danfe_class.return_value = mock_danfe_instance

        mock_danfe_config_class = MagicMock()
        mock_config_instance = MagicMock()
        mock_danfe_config_class.return_value = mock_config_instance

        mock_layout_enum = MagicMock()
        mock_layout_enum.AUTO = "AUTO"

        self.adapter._danfe_class = mock_danfe_class
        self.adapter._danfe_config_class = mock_danfe_config_class
        self.adapter._layout_enum = mock_layout_enum

        # Create minimal NFeData
        nfe_data = NFeData(
            id="35240112345678000123550010000000011234567890",
            version="4.00",
            header=Header(
                state_code=35,
                nf_number=1,
                series=1,
                nature_operation="VENDA",
                model=55,
                issue_date=__import__("datetime").datetime(2024, 1, 15, 10, 0, 0),
                nf_type=1,
                destination_id=1,
                municipality_code=3550308,
                print_format=1,
                emission_type=1,
                check_digit=0,
                environment=2,
                finality=1,
                process_type=0,
                process_version="1.0",
                final_consumer=1,
                presence_indicator=1,
            ),
            emitter=Emitter(
                cnpj="12345678000123",
                company_name="EMPRESA EXEMPLO LTDA",
                address=Address(
                    street="RUA EXEMPLO",
                    number="100",
                    neighborhood="CENTRO",
                    city_code="3550308",
                    city_name="SAO PAULO",
                    state="SP",
                    zip_code="01000000",
                    country_code="1058",
                    country_name="BRASIL",
                ),
                state_registration="123456789012",
                crt=3,
            ),
            recipient=Recipient(
                cnpj="98765432000198",
                name="CLIENTE EXEMPLO LTDA",
                address=Address(
                    street="AV TESTE",
                    number="200",
                    neighborhood="JARDINS",
                    city_code="3550308",
                    city_name="SAO PAULO",
                    state="SP",
                    zip_code="01400000",
                    country_code="1058",
                    country_name="BRASIL",
                ),
                ie_indicator=1,
                state_registration="987654321098",
            ),
            details=[],
            totals=Totals(
                v_bc=Decimal("100.00"),
                v_icms=Decimal("18.00"),
                v_prod=Decimal("100.00"),
                v_nf=Decimal("100.00"),
            ),
        )
        nfe_data._original_xml = b"<xml>original</xml>"

        config = PDFGeneratorConfig(
            layout="auto",
            logo_path=None,
            font_type="times",
            font_size="small",
            margins_mm=(5.0, 5.0, 5.0, 5.0),
            tax_configuration="standard_icms_ipi",
            invoice_display="full_details",
            display_pis_cofins=False,
            watermark_cancelled=True,
            infcpl_semicolon_newline=False,
            receipt_position="top",
            carrier_receipt=False,
            footer_text="",
            footer_height=5.0,
            footer_logo_max_width=20.0,
            footer_spacing=1.0,
        )

        pdf_bytes = self.adapter.generate(nfe_data, config)

        assert pdf_bytes == b"%PDF-1.4 generated content"
        mock_danfe_class.assert_called_once()
        mock_danfe_instance.output.assert_called_once()

    @patch("nfe2pdf.infrastructure.pdf.bfr_adapter.BFRAdapter._init_bfr")
    def test_generate_empty_pdf_raises_error(self, _mock_init_bfr):
        """Test empty PDF from BFR raises error."""
        mock_danfe_class = MagicMock()
        mock_danfe_instance = MagicMock()
        mock_danfe_instance.output.return_value = b""  # Empty PDF
        mock_danfe_class.return_value = mock_danfe_instance

        self.adapter._danfe_class = mock_danfe_class
        self.adapter._danfe_config_class = MagicMock()
        self.adapter._layout_enum = MagicMock()
        self.adapter._layout_enum.AUTO = "AUTO"

        nfe_data = NFeData(
            id="35240112345678000123550010000000011234567890",
            version="4.00",
            header=Header(
                state_code=35,
                nf_number=1,
                series=1,
                nature_operation="VENDA",
                model=55,
                issue_date=__import__("datetime").datetime(2024, 1, 15, 10, 0, 0),
                nf_type=1,
                destination_id=1,
                municipality_code=3550308,
                print_format=1,
                emission_type=1,
                check_digit=0,
                environment=2,
                finality=1,
                process_type=0,
                process_version="1.0",
                final_consumer=1,
                presence_indicator=1,
            ),
            emitter=Emitter(
                cnpj="12345678000123",
                company_name="EMPRESA EXEMPLO LTDA",
                address=Address(
                    street="RUA EXEMPLO",
                    number="100",
                    neighborhood="CENTRO",
                    city_code="3550308",
                    city_name="SAO PAULO",
                    state="SP",
                    zip_code="01000000",
                    country_code="1058",
                    country_name="BRASIL",
                ),
                state_registration="123456789012",
                crt=3,
            ),
            recipient=Recipient(
                cnpj="98765432000198",
                name="CLIENTE EXEMPLO LTDA",
                address=Address(
                    street="AV TESTE",
                    number="200",
                    neighborhood="JARDINS",
                    city_code="3550308",
                    city_name="SAO PAULO",
                    state="SP",
                    zip_code="01400000",
                    country_code="1058",
                    country_name="BRASIL",
                ),
                ie_indicator=1,
                state_registration="987654321098",
            ),
            details=[],
            totals=Totals(
                v_bc=Decimal("100.00"),
                v_icms=Decimal("18.00"),
                v_prod=Decimal("100.00"),
                v_nf=Decimal("100.00"),
            ),
        )
        nfe_data._original_xml = b"<xml>original</xml>"

        config = PDFGeneratorConfig(
            layout="auto",
            logo_path=None,
            font_type="times",
            font_size="small",
            margins_mm=(5.0, 5.0, 5.0, 5.0),
            tax_configuration="standard_icms_ipi",
            invoice_display="full_details",
            display_pis_cofins=False,
            watermark_cancelled=True,
            infcpl_semicolon_newline=False,
            receipt_position="top",
            carrier_receipt=False,
            footer_text="",
            footer_height=5.0,
            footer_logo_max_width=20.0,
            footer_spacing=1.0,
        )

        with pytest.raises(PDFGenerationError) as exc_info:
            self.adapter.generate(nfe_data, config)

        assert "vazio" in str(exc_info.value)

    @patch("nfe2pdf.infrastructure.pdf.bfr_adapter.BFRAdapter._init_bfr")
    def test_generate_missing_original_xml(self, _mock_init_bfr):
        """Test missing original XML raises error."""
        self.adapter._danfe_class = MagicMock()
        self.adapter._danfe_config_class = MagicMock()
        self.adapter._layout_enum = MagicMock()
        self.adapter._layout_enum.AUTO = "AUTO"

        nfe_data = NFeData(
            id="35240112345678000123550010000000011234567890",
            version="4.00",
            header=Header(
                state_code=35,
                nf_number=1,
                series=1,
                nature_operation="VENDA",
                model=55,
                issue_date=__import__("datetime").datetime(2024, 1, 15, 10, 0, 0),
                nf_type=1,
                destination_id=1,
                municipality_code=3550308,
                print_format=1,
                emission_type=1,
                check_digit=0,
                environment=2,
                finality=1,
                process_type=0,
                process_version="1.0",
                final_consumer=1,
                presence_indicator=1,
            ),
            emitter=Emitter(
                cnpj="12345678000123",
                company_name="EMPRESA EXEMPLO LTDA",
                address=Address(
                    street="RUA EXEMPLO",
                    number="100",
                    neighborhood="CENTRO",
                    city_code="3550308",
                    city_name="SAO PAULO",
                    state="SP",
                    zip_code="01000000",
                    country_code="1058",
                    country_name="BRASIL",
                ),
                state_registration="123456789012",
                crt=3,
            ),
            recipient=Recipient(
                cnpj="98765432000198",
                name="CLIENTE EXEMPLO LTDA",
                address=Address(
                    street="AV TESTE",
                    number="200",
                    neighborhood="JARDINS",
                    city_code="3550308",
                    city_name="SAO PAULO",
                    state="SP",
                    zip_code="01400000",
                    country_code="1058",
                    country_name="BRASIL",
                ),
                ie_indicator=1,
                state_registration="987654321098",
            ),
            details=[],
            totals=Totals(
                v_bc=Decimal("100.00"),
                v_icms=Decimal("18.00"),
                v_prod=Decimal("100.00"),
                v_nf=Decimal("100.00"),
            ),
        )
        # No _original_xml attached

        config = PDFGeneratorConfig(
            layout="auto",
            logo_path=None,
            font_type="times",
            font_size="small",
            margins_mm=(5.0, 5.0, 5.0, 5.0),
            tax_configuration="standard_icms_ipi",
            invoice_display="full_details",
            display_pis_cofins=False,
            watermark_cancelled=True,
            infcpl_semicolon_newline=False,
            receipt_position="top",
            carrier_receipt=False,
            footer_text="",
            footer_height=5.0,
            footer_logo_max_width=20.0,
            footer_spacing=1.0,
        )

        with pytest.raises(PDFGenerationError) as exc_info:
            self.adapter.generate(nfe_data, config)

        assert "XML original" in str(exc_info.value) or "original" in str(exc_info.value).lower()

    def test_map_layout(self):
        """Test layout mapping."""
        with patch.object(self.adapter, "_init_bfr"):
            self.adapter._layout_enum = MagicMock()
            self.adapter._layout_enum.AUTO = "AUTO"
            self.adapter._layout_enum.NT_2026_010 = "NT_2026_010"
            self.adapter._layout_enum.MOC_7_0 = "MOC_7_0"

            assert self.adapter._map_layout("auto") == "AUTO"
            assert self.adapter._map_layout("nt_2026_010") == "NT_2026_010"
            assert self.adapter._map_layout("moc_7_0") == "MOC_7_0"
            assert self.adapter._map_layout("unknown") == "AUTO"

    def test_map_font_type(self):
        """Test font type mapping."""
        # Create fresh adapter to avoid already-imported modules
        with patch("nfe2pdf.infrastructure.pdf.bfr_adapter.BFRAdapter._init_bfr"):
            adapter = BFRAdapter()
            mock_font_type = MagicMock()
            mock_font_type.TIMES = "TIMES"
            mock_font_type.COURIER = "COURIER"

            with patch("brazilfiscalreport.danfe.config.FontType", mock_font_type):
                assert adapter._map_font_type("times") == "TIMES"
                assert adapter._map_font_type("TIMES") == "TIMES"
                assert adapter._map_font_type("courier") == "COURIER"
                assert adapter._map_font_type("unknown") == "COURIER"

    def test_map_font_size(self):
        """Test font size mapping."""
        # Create fresh adapter to avoid already-imported modules
        with patch("nfe2pdf.infrastructure.pdf.bfr_adapter.BFRAdapter._init_bfr"):
            adapter = BFRAdapter()
            mock_font_size = MagicMock()
            mock_font_size.SMALL = "SMALL"
            mock_font_size.BIG = "BIG"

            with patch("brazilfiscalreport.danfe.config.FontSize", mock_font_size):
                assert adapter._map_font_size("small") == "SMALL"
                assert adapter._map_font_size("SMALL") == "SMALL"
                assert adapter._map_font_size("big") == "BIG"
                assert adapter._map_font_size("unknown") == "SMALL"

    def test_init_bfr_import_error(self):
        """Test _init_bfr raises PDFGenerationError on ImportError."""
        # The import is: from brazilfiscalreport.danfe import Danfe
        # We need to patch the source module's attribute
        # Since the module might already be loaded, we patch it and force re-import
        import sys

        # Create a mock module that raises ImportError only for specific attributes
        class MockModule:
            def __getattr__(self, name):
                bfr_attrs = (
                    "Danfe",
                    "DanfeConfig",
                    "DanfeLayout",
                    "FontType",
                    "FontSize",
                    "TaxConfiguration",
                    "InvoiceDisplay",
                    "ReceiptPosition",
                    "DecimalConfig",
                    "FooterStamp",
                    "Margins",
                    "ProductDescriptionConfig",
                )
                if name in bfr_attrs:
                    raise ImportError("No module named 'brazilfiscalreport'")
                # For Python's internal module attributes, raise AttributeError
                # to let import machinery handle it
                raise AttributeError(f"module 'brazilfiscalreport' has no attribute '{name}'")

        # Patch the module in sys.modules
        original_modules = {}
        mod_names = [
            "brazilfiscalreport",
            "brazilfiscalreport.danfe",
            "brazilfiscalreport.danfe.config",
        ]
        for mod_name in mod_names:
            if mod_name in sys.modules:
                original_modules[mod_name] = sys.modules[mod_name]
            sys.modules[mod_name] = MockModule()

        try:
            # Now create a fresh adapter - the import inside _init_bfr
            # (called in __init__) will fail
            with pytest.raises(PDFGenerationError) as exc_info:
                BFRAdapter()

            assert "brazilfiscalreport" in str(exc_info.value).lower()
        finally:
            # Restore original modules
            for mod_name in mod_names:
                if mod_name in original_modules:
                    sys.modules[mod_name] = original_modules[mod_name]
                else:
                    del sys.modules[mod_name]
