"""Data Transfer Objects for application layer."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from nfe2pdf.domain.models import NFeData
from nfe2pdf.domain.ports import PDFGeneratorConfig


@dataclass(frozen=True)
class GenerateDanfeInput:
    """Input for GenerateDanfeUseCase."""
    xml_path: Path
    output_path: Optional[Path] = None
    config: Optional[PDFGeneratorConfig] = None
    overwrite: bool = False


@dataclass(frozen=True)
class GenerateDanfeOutput:
    """Output for GenerateDanfeUseCase."""
    pdf_path: Path
    nfe_data: NFeData
    success: bool = True
    error_message: Optional[str] = None


@dataclass(frozen=True)
class InstallAssociationInput:
    """Input for InstallAssociationUseCase."""
    force: bool = False


@dataclass(frozen=True)
class InstallAssociationOutput:
    """Output for InstallAssociationUseCase."""
    success: bool
    message: str