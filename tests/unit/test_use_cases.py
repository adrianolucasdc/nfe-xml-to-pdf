"""Unit tests for use cases."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from nfe2pdf.application import (
    GenerateDanfeInput,
    GenerateDanfeUseCase,
    InstallAssociationInput,
    InstallAssociationUseCase,
)
from nfe2pdf.domain.exceptions import FileAssociationError, PDFGenerationError
from nfe2pdf.domain.models import (
    Address,
    Emitter,
    Header,
    NFeData,
    Recipient,
    Totals,
)
from nfe2pdf.domain.ports import FileAssociationManager, PDFGenerator, XMLParser


class TestGenerateDanfeUseCase:
    """Test GenerateDanfeUseCase."""

    def setup_method(self):
        self.mock_parser = MagicMock(spec=XMLParser)
        self.mock_pdf_generator = MagicMock(spec=PDFGenerator)
        self.mock_validator = MagicMock()
        self.use_case = GenerateDanfeUseCase(
            xml_parser=self.mock_parser,
            pdf_generator=self.mock_pdf_generator,
            validator=self.mock_validator,
        )

    def test_execute_success(self, tmp_path: Path):
        """Test successful DANFE generation."""
        # Setup mocks
        xml_file = tmp_path / "nota.xml"
        xml_file.write_bytes(b"<xml>test</xml>")

        output_file = tmp_path / "nota.pdf"

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

        self.mock_parser.parse_file.return_value = nfe_data
        self.mock_pdf_generator.generate.return_value = b"%PDF-1.4 test pdf content"
        self.mock_validator.validate.return_value = (True, None)

        input_data = GenerateDanfeInput(
            xml_path=xml_file,
            output_path=output_file,
            overwrite=False,
        )

        result = self.use_case.execute(input_data)

        assert result.success is True
        assert result.pdf_path == output_file
        assert result.nfe_data == nfe_data
        assert output_file.exists()
        assert output_file.read_bytes() == b"%PDF-1.4 test pdf content"

        # Verify calls
        self.mock_validator.validate.assert_called_once()
        self.mock_parser.parse_file.assert_called_once_with(xml_file)
        self.mock_pdf_generator.generate.assert_called_once()

    def test_execute_with_default_output_path(self, tmp_path: Path):
        """Test output path defaults to same name with .pdf extension."""
        xml_file = tmp_path / "nota.xml"
        xml_file.write_bytes(b"<xml>test</xml>")

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

        self.mock_parser.parse_file.return_value = nfe_data
        self.mock_pdf_generator.generate.return_value = b"%PDF-1.4 test"
        self.mock_validator.validate.return_value = (True, None)

        input_data = GenerateDanfeInput(
            xml_path=xml_file,
            output_path=None,
            overwrite=False,
        )

        result = self.use_case.execute(input_data)

        expected_output = tmp_path / "nota.pdf"
        assert result.pdf_path == expected_output

    def test_execute_validation_failure(self, tmp_path: Path):
        """Test validation failure raises InvalidXmlError."""
        from nfe2pdf.domain.exceptions import InvalidXmlError

        xml_file = tmp_path / "nota.xml"
        xml_file.write_bytes(b"<xml>test</xml>")

        self.mock_validator.validate.return_value = (False, "Missing required field")

        input_data = GenerateDanfeInput(
            xml_path=xml_file,
            output_path=None,
            overwrite=False,
        )

        with pytest.raises(InvalidXmlError) as exc_info:
            self.use_case.execute(input_data)

        assert "Validação falhou" in str(exc_info.value)

    def test_execute_file_exists_no_overwrite(self, tmp_path: Path):
        """Test file exists and overwrite=False raises PDFGenerationError."""
        xml_file = tmp_path / "nota.xml"
        xml_file.write_bytes(b"<xml>test</xml>")

        output_file = tmp_path / "nota.pdf"
        output_file.write_bytes(b"existing")

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

        self.mock_parser.parse_file.return_value = nfe_data
        self.mock_validator.validate.return_value = (True, None)

        input_data = GenerateDanfeInput(
            xml_path=xml_file,
            output_path=output_file,
            overwrite=False,
        )

        with pytest.raises(PDFGenerationError) as exc_info:
            self.use_case.execute(input_data)

        assert "já existe" in str(exc_info.value)

    def test_execute_file_exists_with_overwrite(self, tmp_path: Path):
        """Test file exists but overwrite=True succeeds."""
        xml_file = tmp_path / "nota.xml"
        xml_file.write_bytes(b"<xml>test</xml>")

        output_file = tmp_path / "nota.pdf"
        output_file.write_bytes(b"existing")

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

        self.mock_parser.parse_file.return_value = nfe_data
        self.mock_pdf_generator.generate.return_value = b"%PDF-1.4 new content"
        self.mock_validator.validate.return_value = (True, None)

        input_data = GenerateDanfeInput(
            xml_path=xml_file,
            output_path=output_file,
            overwrite=True,
        )

        result = self.use_case.execute(input_data)

        assert result.success is True
        assert output_file.read_bytes() == b"%PDF-1.4 new content"

    def test_execute_pdf_generation_error(self, tmp_path: Path):
        """Test PDF generation error is wrapped."""
        xml_file = tmp_path / "nota.xml"
        xml_file.write_bytes(b"<xml>test</xml>")

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

        self.mock_parser.parse_file.return_value = nfe_data
        self.mock_pdf_generator.generate.side_effect = Exception("BFR error")
        self.mock_validator.validate.return_value = (True, None)

        input_data = GenerateDanfeInput(
            xml_path=xml_file,
            output_path=None,
            overwrite=False,
        )

        with pytest.raises(PDFGenerationError) as exc_info:
            self.use_case.execute(input_data)

        assert "Erro inesperado" in str(exc_info.value)


class TestInstallAssociationUseCase:
    """Test InstallAssociationUseCase."""

    def setup_method(self):
        self.mock_manager = MagicMock(spec=FileAssociationManager)
        self.use_case = InstallAssociationUseCase(
            association_manager=self.mock_manager,
        )

    def test_execute_already_exists_no_force(self):
        """Test already associated without force returns success with message."""
        self.mock_manager.is_associated.return_value = True

        input_data = InstallAssociationInput(force=False)

        result = self.use_case.execute(input_data)

        assert result.success is True
        assert "já existe" in result.message
        self.mock_manager.associate.assert_not_called()

    def test_execute_already_exists_with_force(self):
        """Test already associated with force re-associates."""
        self.mock_manager.is_associated.return_value = True

        input_data = InstallAssociationInput(force=True)

        result = self.use_case.execute(input_data)

        assert result.success is True
        self.mock_manager.associate.assert_called_once_with(".xml", "NF-e XML Document")

    def test_execute_not_associated(self):
        """Test not associated installs successfully."""
        self.mock_manager.is_associated.return_value = False

        input_data = InstallAssociationInput(force=False)

        result = self.use_case.execute(input_data)

        assert result.success is True
        assert "sucesso" in result.message
        self.mock_manager.associate.assert_called_once_with(".xml", "NF-e XML Document")

    def test_execute_association_error(self):
        """Test association error is wrapped."""
        self.mock_manager.is_associated.return_value = False
        self.mock_manager.associate.side_effect = FileAssociationError("Permission denied")

        input_data = InstallAssociationInput(force=False)

        with pytest.raises(FileAssociationError):
            self.use_case.execute(input_data)

    def test_execute_unexpected_error(self):
        """Test unexpected error is wrapped."""
        self.mock_manager.is_associated.return_value = False
        self.mock_manager.associate.side_effect = Exception("Unexpected")

        input_data = InstallAssociationInput(force=False)

        with pytest.raises(FileAssociationError) as exc_info:
            self.use_case.execute(input_data)

        assert "Erro inesperado" in str(exc_info.value)
