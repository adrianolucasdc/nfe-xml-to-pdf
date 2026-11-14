"""Use Cases for nfe2pdf application layer."""
from __future__ import annotations

from nfe2pdf.application.dto import (
    GenerateDanfeInput,
    GenerateDanfeOutput,
    InstallAssociationInput,
    InstallAssociationOutput,
)
from nfe2pdf.config import get_settings
from nfe2pdf.domain.exceptions import (
    FileAssociationError,
    InvalidXmlError,
    NotNFeError,
    PDFGenerationError,
)
from nfe2pdf.domain.ports import FileAssociationManager, PDFGenerator, XMLParser


class GenerateDanfeUseCase:
    """Use case for generating DANFE PDF from NF-e XML."""

    def __init__(
        self,
        xml_parser: XMLParser,
        pdf_generator: PDFGenerator,
        validator: object | None = None,  # NFexmlValidator - using object to avoid circular import
    ) -> None:
        self._xml_parser = xml_parser
        self._pdf_generator = pdf_generator
        self._validator = validator

    def execute(self, input_data: GenerateDanfeInput) -> GenerateDanfeOutput:
        """Execute the use case."""
        try:
            # 1. Validate XML if validator provided
            if self._validator is not None:
                xml_content = input_data.xml_path.read_bytes()
                is_valid, error = self._validator.validate(xml_content)
                if not is_valid:
                    raise InvalidXmlError(f"Validação falhou: {error}")

            # 2. Parse XML
            nfe_data = self._xml_parser.parse_file(input_data.xml_path)

            # 3. Attach original XML for PDF generator (BFRAdapter needs raw XML)
            nfe_data._original_xml = input_data.xml_path.read_bytes()

            # 4. Determine output path
            output_path = input_data.output_path
            if output_path is None:
                output_path = input_data.xml_path.with_suffix(".pdf")

            # 5. Check overwrite
            if output_path.exists() and not input_data.overwrite:
                raise PDFGenerationError(
                    f"Arquivo já existe: {output_path}. Use overwrite=True para sobrescrever."
                )

            # 6. Get configuration
            config = input_data.config
            if config is None:
                settings = get_settings()
                config = settings.get_pdf_generator_config()

            # 7. Generate PDF
            pdf_bytes = self._pdf_generator.generate(nfe_data, config)

            # 8. Save PDF
            output_path.write_bytes(pdf_bytes)

            return GenerateDanfeOutput(
                pdf_path=output_path,
                nfe_data=nfe_data,
                success=True,
            )

        except (InvalidXmlError, NotNFeError, PDFGenerationError):
            raise
        except OSError as e:
            raise PDFGenerationError(f"Erro de I/O: {e}", original_error=e) from e
        except Exception as e:
            raise PDFGenerationError(f"Erro inesperado: {e}", original_error=e) from e


class InstallAssociationUseCase:
    """Use case for installing Windows file association."""

    def __init__(self, association_manager: FileAssociationManager) -> None:
        self._association_manager = association_manager

    def execute(self, input_data: InstallAssociationInput) -> InstallAssociationOutput:
        """Execute the use case."""
        try:
            if self._association_manager.is_associated(".xml") and not input_data.force:
                return InstallAssociationOutput(
                    success=True,
                    message="Associação .xml já existe. Use --force para reinstalar."
                )

            self._association_manager.associate(".xml", "NF-e XML Document")

            return InstallAssociationOutput(
                success=True,
                message="Associação .xml instalada com sucesso."
            )

        except FileAssociationError:
            raise
        except Exception as e:
            raise FileAssociationError(
                f"Erro inesperado ao instalar associação: {e}", original_error=e
            ) from e