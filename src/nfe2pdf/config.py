"""Configuration management using Pydantic Settings (YAML + env vars)."""
from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from nfe2pdf.domain.ports import PDFGeneratorConfig
from nfe2pdf.utils.paths import ensure_config_dir, get_config_path, get_logo_path


class DanfeSettings(BaseSettings):
    """DANFE generation settings (maps to PDFGeneratorConfig)."""

    layout: str = Field(default="auto", description="Layout: auto | nt_2026_010 | moc_7_0")
    logo: str | None = Field(default=None, description="Caminho absoluto para logo .png/.jpg")
    margins_top: float = Field(default=5.0, alias="margins.top")
    margins_right: float = Field(default=5.0, alias="margins.right")
    margins_bottom: float = Field(default=5.0, alias="margins.bottom")
    margins_left: float = Field(default=5.0, alias="margins.left")
    font_type: str = Field(default="times", description="times | courier")
    font_size: str = Field(default="small", description="small | big")
    tax_configuration: str = Field(default="standard_icms_ipi")
    invoice_display: str = Field(default="full_details")
    display_pis_cofins: bool = Field(default=False)
    watermark_cancelled: bool = Field(default=True)
    infcpl_semicolon_newline: bool = Field(default=False)
    receipt_position: str = Field(default="top")
    carrier_receipt: bool = Field(default=False)
    footer_text: str = Field(default="")
    footer_logo: str | None = Field(default=None)
    footer_height: float = Field(default=5.0)
    footer_logo_max_width: float = Field(default=20.0)
    footer_spacing: float = Field(default=1.0)

    def to_pdf_generator_config(self) -> PDFGeneratorConfig:
        """Convert to domain PDFGeneratorConfig."""
        # Resolve logo path: explicit > default package logo
        logo_path = self.logo
        if logo_path is None:
            logo_path = str(get_logo_path()) if get_logo_path() else None

        footer_logo_path = self.footer_logo
        if footer_logo_path is None and self.footer_text:
            # Se tem texto mas não logo no footer, usa a logo principal se houver
            footer_logo_path = logo_path

        return PDFGeneratorConfig(
            layout=self.layout,
            logo_path=logo_path,
            margins_mm=(
                self.margins_top,
                self.margins_right,
                self.margins_bottom,
                self.margins_left,
            ),
            font_type=self.font_type,
            font_size=self.font_size,
            tax_configuration=self.tax_configuration,
            invoice_display=self.invoice_display,
            display_pis_cofins=self.display_pis_cofins,
            watermark_cancelled=self.watermark_cancelled,
            infcpl_semicolon_newline=self.infcpl_semicolon_newline,
            receipt_position=self.receipt_position,
            carrier_receipt=self.carrier_receipt,
            footer_text=self.footer_text,
            footer_logo=footer_logo_path,
            footer_height=self.footer_height,
            footer_logo_max_width=self.footer_logo_max_width,
            footer_spacing=self.footer_spacing,
        )


class LoggingSettings(BaseSettings):
    """Logging settings."""

    level: str = Field(default="INFO", description="Log level: DEBUG | INFO | WARNING | ERROR")
    file: str | None = Field(default=None, description="Log file path (None = console only)")
    rotation: str = Field(default="10 MB")
    retention: str = Field(default="7 days")


class OutputSettings(BaseSettings):
    """Output settings."""

    default_dir: str | None = Field(
        default=None, description="Default output dir for PDFs (None = same dir as XML)"
    )
    overwrite: bool = Field(default=False, description="Overwrite existing file without asking")


class Settings(BaseSettings):
    """Main application settings loaded from YAML + environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="NFE2PDF_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    danfe: DanfeSettings = Field(default_factory=DanfeSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    output: OutputSettings = Field(default_factory=OutputSettings)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Customize settings sources to include YAML file.

        Priority order (later overrides earlier):
        1. init_settings (defaults)
        2. YAML file
        3. Environment variables (NFE2PDF_*)
        4. .env file
        5. File secrets
        """
        yaml_path = get_config_path()
        return (
            init_settings,
            env_settings,  # Env vars override YAML
            YamlConfigSettingsSource(settings_cls, yaml_file=yaml_path, yaml_file_encoding="utf-8"),
            dotenv_settings,
            file_secret_settings,
        )

    @classmethod
    def load(cls) -> Settings:
        """Load settings from config file and environment."""
        ensure_config_dir()
        return cls()

    def save(self, path: Path | None = None) -> None:
        """Save current settings to YAML file."""
        import yaml

        config_path = path or get_config_path()
        ensure_config_dir()

        # Convert to dict excluding None values for cleaner YAML
        data = self.model_dump(exclude_none=True)

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)

    def get_pdf_generator_config(self) -> PDFGeneratorConfig:
        """Get PDF generator config from danfe settings."""
        return self.danfe.to_pdf_generator_config()


# Global settings instance (lazy loaded)
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get global settings instance (singleton pattern)."""
    global _settings
    if _settings is None:
        _settings = Settings.load()
    return _settings


def reload_settings() -> Settings:
    """Force reload settings from file/env."""
    global _settings
    _settings = Settings.load()
    return _settings