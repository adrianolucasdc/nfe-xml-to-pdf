"""CLI module for nfe2pdf (stub - implementado no Commit 8)."""
from __future__ import annotations

import click


@click.group()
@click.version_option(version="0.1.0", prog_name="nfe2pdf")
def main() -> None:
    """nfe2pdf - Conversor NF-e XML para PDF (DANFE)."""
    pass


@main.command()
@click.argument("xml_file", type=click.Path(exists=True, path_type=str))
def generate(xml_file: str) -> None:
    """Gerar DANFE a partir de arquivo XML de NF-e."""
    click.echo(f"⚠️  Comando 'generate' será implementado no Commit 8")
    click.echo(f"    Arquivo: {xml_file}")


@main.command()
def config() -> None:
    """Mostrar configuração atual."""
    click.echo("⚠️  Comando 'config' será implementado no Commit 8")


@main.command()
def install() -> None:
    """Instalar associação de arquivo .xml no Windows."""
    click.echo("⚠️  Comando 'install' será implementado no Commit 13")


if __name__ == "__main__":
    main()