"""CLI for nfe2pdf - Conversor NF-e XML para PDF (DANFE)."""

from __future__ import annotations

import sys
from pathlib import Path

import click
from loguru import logger

from nfe2pdf import __version__
from nfe2pdf.application import (
    GenerateDanfeInput,
    GenerateDanfeUseCase,
)
from nfe2pdf.config import get_settings
from nfe2pdf.domain.exceptions import (
    FileAssociationError,
    InvalidXmlError,
    NFe2PDFError,
    NotNFeError,
    PDFGenerationError,
)
from nfe2pdf.infrastructure import (
    NFexmlParser,
    NFexmlValidator,
    create_pdf_generator,
)

# Configure logger
logger.remove()
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
)


def setup_logging(level: str = "INFO") -> None:
    """Configure logging level."""
    logger.remove()
    fmt = "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>"
    logger.add(sys.stderr, level=level.upper(), format=fmt)


def handle_error(e: Exception, ctx: click.Context) -> None:
    """Handle exceptions and exit with appropriate code."""
    if isinstance(e, NFe2PDFError):
        logger.error(str(e))
        if hasattr(e, "original_error") and e.original_error:
            logger.debug(f"Original error: {e.original_error}")
    else:
        logger.exception("Erro inesperado")
    ctx.exit(1)


@click.group()
@click.version_option(version=__version__, prog_name="nfe2pdf")
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    help="Nível de log",
)
@click.pass_context
def main(ctx: click.Context, log_level: str) -> None:
    """nfe2pdf - Conversor NF-e XML para PDF (DANFE).

    Gera DANFE oficial (layout NT 2026.010) a partir de arquivos XML de NF-e.
    Suporta associação de arquivo .xml no Windows para duplo-clique direto.

    Uso direto (para "Abrir com..." do Windows):
        nfe2pdf.exe "C:\\caminho\\nota.xml"
    """
    setup_logging(log_level)
    ctx.ensure_object(dict)


@main.command()
@click.argument(
    "xml_file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
)
@click.option(
    "-o",
    "--output",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Caminho do arquivo PDF de saída (padrão: mesmo nome do XML com extensão .pdf)",
)
@click.option(
    "--overwrite/--no-overwrite",
    default=False,
    help="Sobrescrever arquivo PDF existente sem perguntar",
)
@click.option(
    "--layout",
    type=click.Choice(["auto", "nt_2026_010", "moc_7_0"], case_sensitive=False),
    help="Layout do DANFE (sobrescreve configuração)",
)
@click.option(
    "--logo",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Logo da empresa para o DANFE (sobrescreve configuração)",
)
@click.option(
    "--font-type",
    type=click.Choice(["times", "courier"], case_sensitive=False),
    help="Fonte do DANFE (sobrescreve configuração)",
)
@click.option(
    "--font-size",
    type=click.Choice(["small", "big"], case_sensitive=False),
    help="Tamanho da fonte (sobrescreve configuração)",
)
@click.option(
    "--no-watermark",
    is_flag=True,
    help="Não mostrar marca d'água 'CANCELADA' em NF-e canceladas",
)
@click.option(
    "--validate/--no-validate",
    default=True,
    help="Validar XML antes de gerar PDF",
)
@click.pass_context
def generate(
    ctx: click.Context,
    xml_file: Path,
    output: Path | None,
    overwrite: bool,
    layout: str | None,
    logo: Path | None,
    font_type: str | None,
    font_size: str | None,
    no_watermark: bool,
    validate: bool,
) -> None:
    """Gerar DANFE PDF a partir de arquivo XML de NF-e.

    Exemplo:
        nfe2pdf generate nota.xml
        nfe2pdf generate nota.xml -o danfe.pdf --layout nt_2026_010
    """
    try:
        # Load settings
        settings = get_settings()
        pdf_config = settings.get_pdf_generator_config()

        # Apply CLI overrides
        if layout:
            pdf_config.layout = layout
        if logo:
            pdf_config.logo_path = str(logo)
        if font_type:
            pdf_config.font_type = font_type
        if font_size:
            pdf_config.font_size = font_size
        if no_watermark:
            pdf_config.watermark_cancelled = False

        # Initialize dependencies
        parser = NFexmlParser()
        validator = NFexmlValidator() if validate else None
        pdf_generator = create_pdf_generator()

        use_case = GenerateDanfeUseCase(parser, pdf_generator, validator)

        # Prepare input
        input_data = GenerateDanfeInput(
            xml_path=xml_file,
            output_path=output,
            config=pdf_config,
            overwrite=overwrite,
        )

        # Execute
        logger.info(f"Processando: {xml_file}")
        result = use_case.execute(input_data)

        logger.success(f"DANFE gerado: {result.pdf_path}")
        key = result.nfe_data.formatted_access_key
        logger.info(f"NF-e: {result.nfe_data.emitter.company_name} | Chave: {key}")

        if result.nfe_data.is_cancelled:
            logger.warning("NF-e CANCELADA - marca d'água aplicada")

    except (InvalidXmlError, NotNFeError, PDFGenerationError) as e:
        handle_error(e, ctx)
    except Exception:
        logger.exception("Erro inesperado")
        ctx.exit(1)


@main.command()
@click.option(
    "--show-path",
    is_flag=True,
    help="Mostrar apenas o caminho do arquivo de configuração",
)
@click.option(
    "--edit",
    is_flag=True,
    help="Abrir arquivo de configuração no editor padrão",
)
@click.option(
    "--reset",
    is_flag=True,
    help="Restaurar configuração padrão",
)
def config(show_path: bool, edit: bool, reset: bool) -> None:
    """Gerenciar configuração do nfe2pdf.

    A configuração é salva em %APPDATA%\\nfe2pdf\\config.yaml
    e pode ser sobrescrita por variáveis de ambiente NFE2PDF_*.
    """
    import os
    import subprocess

    from nfe2pdf.utils.paths import get_config_path

    config_path = get_config_path()

    if show_path:
        click.echo(str(config_path))
        return

    if reset:
        if config_path.exists():
            config_path.unlink()
            click.echo("Configuração restaurada para padrão")
        else:
            click.echo("Nenhuma configuração personalizada encontrada")
        return

    if edit:
        if not config_path.exists():
            # Create default config
            settings = get_settings()
            settings.save()
        try:
            if sys.platform == "win32":
                os.startfile(str(config_path))  # type: ignore
            else:
                subprocess.run(["xdg-open", str(config_path)], check=False)
        except Exception as e:
            logger.error(f"Não foi possível abrir editor: {e}")
        return

    # Show current config
    settings = get_settings()
    import yaml

    dumped = yaml.dump(settings.model_dump(exclude_none=True), allow_unicode=True, sort_keys=False)
    click.echo(f"Arquivo: {config_path}")
    click.echo("---")
    click.echo(dumped)


@main.command()
@click.option(
    "--force",
    is_flag=True,
    help="Forçar reinstalação mesmo se já associado",
)
@click.option(
    "--check",
    is_flag=True,
    help="Apenas verificar se a associação existe",
)
@click.pass_context
def install(ctx: click.Context, force: bool, check: bool) -> None:
    """Instalar associação de arquivo .xml no Windows.

    Registra o nfe2pdf como manipulador padrão para arquivos .xml,
    permitindo gerar DANFE com duplo-clique no arquivo XML.
    """
    from nfe2pdf.infrastructure.windows.registry import WindowsRegistryManager

    try:
        manager = WindowsRegistryManager()

        if check:
            if manager.is_associated(".xml"):
                click.echo("[OK] Associacao .xml ja esta instalada")
            else:
                click.echo("[ERRO] Associacao .xml NAO esta instalada")
            return

        if manager.is_associated(".xml") and not force:
            click.echo("Associacao .xml ja existe. Use --force para reinstalar.")
            return

        click.echo("Instalando associacao .xml...")
        manager.associate(".xml", "NF-e XML Document")
        click.echo("[OK] Associacao instalada com sucesso!")
        click.echo("Agora voce pode dar duplo-clique em arquivos .xml para gerar o DANFE.")

    except FileAssociationError as e:
        handle_error(e, ctx)
    except Exception:
        logger.exception("Erro inesperado")
        ctx.exit(1)
