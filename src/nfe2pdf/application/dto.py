"""Data Transfer Objects for application layer."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from nfe2pdf.domain.models import NFeData
from nfe2pdf.domain.ports import PDFGeneratorConfig


@dataclass(frozen=True)
class GenerateDanfeInput:
    """Input for GenerateDanfeUseCase."""

    xml_path: Path
    output_path: Path | None = None
    config: PDFGeneratorConfig | None = None
    overwrite: bool = False


@dataclass(frozen=True)
class GenerateDanfeOutput:
    """Output for GenerateDanfeUseCase."""

    pdf_path: Path
    nfe_data: NFeData
    success: bool = True
    error_message: str | None = None


@dataclass(frozen=True)
class InstallAssociationInput:
    """Input for InstallAssociationUseCase."""

    force: bool = False


@dataclass(frozen=True)
class InstallAssociationOutput:
    """Output for InstallAssociationUseCase."""

    success: bool
    message: str
