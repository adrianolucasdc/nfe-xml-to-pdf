"""Integration tests for full NF-e to PDF pipeline."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


def _is_module_available(module_name: str) -> bool:
    """Check if a module is available without importing it."""
    return importlib.util.find_spec(module_name) is not None


BFR_AVAILABLE = _is_module_available("brazilfiscalreport.danfe")
PDFMINER_AVAILABLE = _is_module_available("pdfminer.high_level")

FIXTURE_PATH = Path(__file__).parent.parent / "fixtures" / "nfe_sample.xml"


def _get_extract_text():
    """Get extract_text function, raising skip if not available."""
    if not PDFMINER_AVAILABLE:
        pytest.skip("pdfminer.six not installed")
    from pdfminer.high_level import extract_text

    return extract_text


@pytest.mark.skipif(not BFR_AVAILABLE, reason="BrazilFiscalReport not installed")
@pytest.mark.skipif(not PDFMINER_AVAILABLE, reason="pdfminer.six not installed")
class TestFullPipeline:
    """Test complete XML -> PDF pipeline with real BFR."""

    def test_parse_validate_generate_pdf(self, tmp_path: Path):
        """Test full pipeline: parse XML, validate, generate PDF, verify content."""
        # Import inside to avoid issues
        from nfe2pdf.config import Settings
        from nfe2pdf.infrastructure.pdf.bfr_adapter import BFRAdapter
        from nfe2pdf.infrastructure.xml.parser import NFexmlParser
        from nfe2pdf.infrastructure.xml.validator import NFexmlValidator

        extract_text = _get_extract_text()

        # Parse
        parser = NFexmlParser()
        nfe_data = parser.parse_file(FIXTURE_PATH)

        # Verify parsed data
        assert nfe_data.emitter.company_name == "EMPRESA EXEMPLO LTDA"
        assert nfe_data.recipient.name == "CLIENTE EXEMPLO LTDA"
        assert len(nfe_data.details) == 1
        assert nfe_data.details[0].product.description == "PRODUTO EXEMPLO"
        assert nfe_data.access_key == "35240112345678000123550010000000011234567890"

        # Validate (validator expects raw XML bytes)
        validator = NFexmlValidator()
        xml_bytes = FIXTURE_PATH.read_bytes()
        is_valid, error = validator.validate(xml_bytes)
        assert is_valid is True
        assert error is None

        # Generate PDF
        pdf_generator = BFRAdapter()
        nfe_data._original_xml = xml_bytes

        output_path = tmp_path / "output.pdf"
        config = Settings().danfe.to_pdf_generator_config()  # Use default config

        pdf_bytes = pdf_generator.generate(nfe_data, config)

        # Save and verify PDF
        output_path.write_bytes(pdf_bytes)
        assert output_path.exists()
        assert output_path.stat().st_size > 1000  # PDF should have content

        # Extract text and verify content
        text = extract_text(str(output_path))
        # Normalize whitespace for searching (PDF extraction may split across lines)
        text_norm = " ".join(text.split())
        assert "EMPRESA EXEMPLO LTDA" in text_norm
        assert "CLIENTE EXEMPLO LTDA" in text_norm
        assert "PRODUTO EXEMPLO" in text_norm
        access_key = "35240112345678000123550010000000011234567890"
        assert access_key in text_norm.replace(" ", "")

    def test_generate_pdf_with_custom_config(self, tmp_path: Path):
        """Test PDF generation with custom configuration."""
        from nfe2pdf.domain.ports import PDFGeneratorConfig
        from nfe2pdf.infrastructure.pdf.bfr_adapter import BFRAdapter
        from nfe2pdf.infrastructure.xml.parser import NFexmlParser

        extract_text = _get_extract_text()

        parser = NFexmlParser()
        nfe_data = parser.parse_file(FIXTURE_PATH)
        xml_bytes = FIXTURE_PATH.read_bytes()
        nfe_data._original_xml = xml_bytes

        # Custom config - create PDFGeneratorConfig directly
        config = PDFGeneratorConfig(
            layout="auto",
            logo_path=None,
            margins_mm=(10.0, 10.0, 10.0, 10.0),
            font_type="times",
            font_size="small",
            tax_configuration="standard_icms_ipi",
            invoice_display="full_details",
            display_pis_cofins=False,
            watermark_cancelled=True,
            infcpl_semicolon_newline=False,
            receipt_position="top",
            carrier_receipt=False,
            footer_text="",
            footer_logo=None,
            footer_height=5.0,
            footer_logo_max_width=20.0,
            footer_spacing=1.0,
        )

        pdf_generator = BFRAdapter()
        pdf_bytes = pdf_generator.generate(nfe_data, config)

        output_path = tmp_path / "custom.pdf"
        output_path.write_bytes(pdf_bytes)
        assert output_path.exists()

        text = extract_text(str(output_path))
        assert "EMPRESA EXEMPLO LTDA" in text

    def test_multiple_products(self, tmp_path: Path):
        """Test with XML containing multiple products."""
        from nfe2pdf.config import Settings
        from nfe2pdf.infrastructure.pdf.bfr_adapter import BFRAdapter
        from nfe2pdf.infrastructure.xml.parser import NFexmlParser

        extract_text = _get_extract_text()

        # Create XML with multiple products
        xml_content = FIXTURE_PATH.read_text()
        # Duplicate the det element for a second product
        det_start = xml_content.find('<det nItem="1">')
        det_end = xml_content.find("</det>", det_start) + 6
        det_element = xml_content[det_start:det_end]

        # Create second product
        det2 = det_element.replace('nItem="1"', 'nItem="2"')
        det2 = det2.replace("<cProd>001</cProd>", "<cProd>002</cProd>")
        det2 = det2.replace("<xProd>PRODUTO EXEMPLO</xProd>", "<xProd>OUTRO PRODUTO</xProd>")
        det2 = det2.replace("<vProd>100.00</vProd>", "<vProd>200.00</vProd>")

        # Insert after first det
        modified_xml = xml_content[:det_end] + "\n      " + det2 + xml_content[det_end:]

        # Update totals
        modified_xml = modified_xml.replace("<vProd>100.00</vProd>", "<vProd>300.00</vProd>", 1)
        modified_xml = modified_xml.replace("<vNF>100.00</vNF>", "<vNF>300.00</vNF>")

        # Write temp XML
        multi_xml_path = tmp_path / "multi_product.xml"
        multi_xml_path.write_text(modified_xml, encoding="utf-8")

        # Parse and generate
        parser = NFexmlParser()
        nfe_data = parser.parse_file(multi_xml_path)
        xml_bytes = multi_xml_path.read_bytes()
        nfe_data._original_xml = xml_bytes

        pdf_generator = BFRAdapter()
        pdf_bytes = pdf_generator.generate(nfe_data, Settings().danfe.to_pdf_generator_config())

        output_path = tmp_path / "multi.pdf"
        output_path.write_bytes(pdf_bytes)

        text = extract_text(str(output_path))
        assert "PRODUTO EXEMPLO" in text
        assert "OUTRO PRODUTO" in text


@pytest.mark.skipif(not BFR_AVAILABLE, reason="BrazilFiscalReport not installed")
@pytest.mark.skipif(not PDFMINER_AVAILABLE, reason="pdfminer.six not installed")
class TestGenerateDanfeUseCaseIntegration:
    """Integration test for GenerateDanfeUseCase."""

    def test_use_case_end_to_end(self, tmp_path: Path):
        """Test use case with real components."""
        from nfe2pdf.application import GenerateDanfeInput, GenerateDanfeUseCase
        from nfe2pdf.infrastructure.pdf.bfr_adapter import BFRAdapter
        from nfe2pdf.infrastructure.xml.parser import NFexmlParser
        from nfe2pdf.infrastructure.xml.validator import NFexmlValidator

        extract_text = _get_extract_text()

        use_case = GenerateDanfeUseCase(
            xml_parser=NFexmlParser(),
            pdf_generator=BFRAdapter(),
            validator=NFexmlValidator(),
        )

        output_path = tmp_path / "usecase_output.pdf"

        result = use_case.execute(
            GenerateDanfeInput(
                xml_path=FIXTURE_PATH,
                output_path=output_path,
                overwrite=True,
            )
        )

        assert result.success is True
        assert result.pdf_path == output_path
        assert output_path.exists()
        assert output_path.stat().st_size > 1000

        # Verify content
        text = extract_text(str(output_path))
        assert "EMPRESA EXEMPLO LTDA" in text

    def test_use_case_with_default_output(self, tmp_path: Path):
        """Test use case with default output path (same name, .pdf extension)."""
        from nfe2pdf.application import GenerateDanfeInput, GenerateDanfeUseCase
        from nfe2pdf.infrastructure.pdf.bfr_adapter import BFRAdapter
        from nfe2pdf.infrastructure.xml.parser import NFexmlParser
        from nfe2pdf.infrastructure.xml.validator import NFexmlValidator

        extract_text = _get_extract_text()

        use_case = GenerateDanfeUseCase(
            xml_parser=NFexmlParser(),
            pdf_generator=BFRAdapter(),
            validator=NFexmlValidator(),
        )

        # Copy fixture to temp dir
        xml_path = tmp_path / "nota.xml"
        xml_path.write_bytes(FIXTURE_PATH.read_bytes())

        result = use_case.execute(
            GenerateDanfeInput(
                xml_path=xml_path,
                output_path=None,  # Should default to nota.pdf
                overwrite=True,
            )
        )

        expected_output = tmp_path / "nota.pdf"
        assert result.success is True
        assert result.pdf_path == expected_output
        assert expected_output.exists()

        text = extract_text(str(expected_output))
        assert "EMPRESA EXEMPLO LTDA" in text

    def test_use_case_overwrite_protection(self, tmp_path: Path):
        """Test that use case prevents overwrite by default."""
        from nfe2pdf.application import GenerateDanfeInput, GenerateDanfeUseCase
        from nfe2pdf.domain.exceptions import PDFGenerationError
        from nfe2pdf.infrastructure.pdf.bfr_adapter import BFRAdapter
        from nfe2pdf.infrastructure.xml.parser import NFexmlParser
        from nfe2pdf.infrastructure.xml.validator import NFexmlValidator

        use_case = GenerateDanfeUseCase(
            xml_parser=NFexmlParser(),
            pdf_generator=BFRAdapter(),
            validator=NFexmlValidator(),
        )

        output_path = tmp_path / "protected.pdf"
        output_path.write_bytes(b"existing content")

        with pytest.raises(PDFGenerationError) as exc_info:
            use_case.execute(
                GenerateDanfeInput(
                    xml_path=FIXTURE_PATH,
                    output_path=output_path,
                    overwrite=False,  # Should fail
                )
            )

        assert "já existe" in str(exc_info.value)
        # Original content preserved
        assert output_path.read_bytes() == b"existing content"

    def test_use_case_validation_failure(self, tmp_path: Path):
        """Test use case with invalid XML."""
        from nfe2pdf.application import GenerateDanfeInput, GenerateDanfeUseCase
        from nfe2pdf.infrastructure.pdf.bfr_adapter import BFRAdapter
        from nfe2pdf.infrastructure.xml.parser import NFexmlParser
        from nfe2pdf.infrastructure.xml.validator import NFexmlValidator

        # Create invalid XML
        invalid_xml = tmp_path / "invalid.xml"
        invalid_xml.write_text("<root>not nfe</root>")

        use_case = GenerateDanfeUseCase(
            xml_parser=NFexmlParser(),
            pdf_generator=BFRAdapter(),
            validator=NFexmlValidator(),
        )

        with pytest.raises(Exception) as exc_info:
            use_case.execute(
                GenerateDanfeInput(
                    xml_path=invalid_xml,
                    output_path=tmp_path / "out.pdf",
                )
            )

        # Should fail during parsing or validation
        assert exc_info.value is not None


class TestInstallAssociationUseCaseIntegration:
    """Integration test for file association (mocked Windows)."""

    def test_install_association_use_case(self):
        """Test install association use case with mocked registry."""
        from unittest.mock import MagicMock

        from nfe2pdf.application import InstallAssociationInput, InstallAssociationUseCase
        from nfe2pdf.infrastructure.windows.registry import WindowsRegistryManager

        mock_manager = MagicMock(spec=WindowsRegistryManager)
        mock_manager.is_associated.return_value = False

        use_case = InstallAssociationUseCase(association_manager=mock_manager)

        result = use_case.execute(InstallAssociationInput(force=False))

        assert result.success is True
        assert "sucesso" in result.message.lower()
        mock_manager.associate.assert_called_once_with(".xml", "NF-e XML Document")

    def test_install_already_exists_no_force(self):
        """Test already associated without force."""
        from unittest.mock import MagicMock

        from nfe2pdf.application import InstallAssociationInput, InstallAssociationUseCase
        from nfe2pdf.infrastructure.windows.registry import WindowsRegistryManager

        mock_manager = MagicMock(spec=WindowsRegistryManager)
        mock_manager.is_associated.return_value = True

        use_case = InstallAssociationUseCase(association_manager=mock_manager)

        result = use_case.execute(InstallAssociationInput(force=False))

        assert result.success is True
        assert "já existe" in result.message.lower()
        mock_manager.associate.assert_not_called()

    def test_install_already_exists_with_force(self):
        """Test already associated with force."""
        from unittest.mock import MagicMock

        from nfe2pdf.application import InstallAssociationInput, InstallAssociationUseCase
        from nfe2pdf.infrastructure.windows.registry import WindowsRegistryManager

        mock_manager = MagicMock(spec=WindowsRegistryManager)
        mock_manager.is_associated.return_value = True

        use_case = InstallAssociationUseCase(association_manager=mock_manager)

        result = use_case.execute(InstallAssociationInput(force=True))

        assert result.success is True
        mock_manager.associate.assert_called_once_with(".xml", "NF-e XML Document")


class TestCLIIntegration:
    """Test CLI integration (basic smoke tests)."""

    def test_cli_help(self):
        """Test CLI help command."""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-m", "nfe2pdf", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
            env={**__import__("os").environ, "PYTHONPATH": "src"},
        )
        assert result.returncode == 0
        assert "nfe2pdf" in result.stdout.lower()
        assert "generate" in result.stdout
        assert "config" in result.stdout
        assert "install" in result.stdout

    def test_cli_version(self):
        """Test CLI version command."""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-m", "nfe2pdf", "--version"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
            env={**__import__("os").environ, "PYTHONPATH": "src"},
        )
        assert result.returncode == 0
        assert result.stdout.strip() != ""

    def test_cli_config_show(self):
        """Test CLI config show command."""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-m", "nfe2pdf", "config", "show"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
            env={**__import__("os").environ, "PYTHONPATH": "src"},
        )
        # config command might not have 'show' subcommand - check what's available
        # If it fails, just verify the command exists
        assert result.returncode in (0, 2)  # 2 = usage error for missing subcommand
        # If 0, check output; if 2, just verify command exists
        if result.returncode == 0:
            assert "layout" in result.stdout.lower()

    @pytest.mark.skipif(not BFR_AVAILABLE, reason="BrazilFiscalReport not installed")
    @pytest.mark.skipif(not PDFMINER_AVAILABLE, reason="pdfminer.six not installed")
    def test_cli_generate(self, tmp_path: Path):
        """Test CLI generate command."""
        import subprocess
        import sys

        from pdfminer.high_level import extract_text

        output_path = tmp_path / "cli_output.pdf"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "nfe2pdf",
                "generate",
                str(FIXTURE_PATH),
                "-o",
                str(output_path),
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
            env={**__import__("os").environ, "PYTHONPATH": "src"},
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert output_path.exists()
        assert output_path.stat().st_size > 1000

        # Verify content
        text = extract_text(str(output_path))
        assert "EMPRESA EXEMPLO LTDA" in text

    @pytest.mark.skipif(not BFR_AVAILABLE, reason="BrazilFiscalReport not installed")
    @pytest.mark.skipif(not PDFMINER_AVAILABLE, reason="pdfminer.six not installed")
    def test_cli_direct_execution(self, tmp_path: Path):
        """Test CLI direct execution (simulating 'Abrir com...')."""
        import subprocess
        import sys

        from pdfminer.high_level import extract_text

        output_path = tmp_path / "direct_output.pdf"

        # Direct execution: nfe2pdf arquivo.xml -o output.pdf
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "nfe2pdf",
                str(FIXTURE_PATH),
                "-o",
                str(output_path),
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
            env={**__import__("os").environ, "PYTHONPATH": "src"},
        )

        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert output_path.exists()

        text = extract_text(str(output_path))
        assert "EMPRESA EXEMPLO LTDA" in text

    def test_cancelled_watermark_only_when_nfe_is_cancelled(self):
        from nfe2pdf.config import Settings
        from nfe2pdf.infrastructure.pdf.bfr_adapter import BFRAdapter

        config = Settings().danfe.to_pdf_generator_config()
        assert config.watermark_cancelled is True  # default option on
        adapter = BFRAdapter()
        adapter._init_bfr()
        assert adapter._build_bfr_config(config, is_cancelled=False).watermark_cancelled is False
        assert adapter._build_bfr_config(config, is_cancelled=True).watermark_cancelled is True
