"""ConfigManager implementation using Pydantic Settings."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from nfe2pdf.config import Settings, get_settings, reload_settings
from nfe2pdf.domain.ports import ConfigManager


class PydanticConfigManager:
    """ConfigManager implementation using Pydantic Settings (YAML + env vars)."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def load(self) -> dict[str, Any]:
        """Load configuration as dictionary."""
        return self._settings.model_dump(exclude_none=True)

    def save(self, config: dict[str, Any]) -> None:
        """Save configuration to YAML file."""
        # Update settings with new values
        for key, value in config.items():
            if hasattr(self._settings, key):
                setattr(self._settings, key, value)
        self._settings.save()

    def get_default_config(self) -> dict[str, Any]:
        """Get default configuration."""
        default_settings = Settings()
        return default_settings.model_dump(exclude_none=True)

    @property
    def settings(self) -> Settings:
        """Access underlying Settings instance."""
        return self._settings

    def get_pdf_generator_config(self):
        """Get PDF generator config."""
        return self._settings.get_pdf_generator_config()


def create_config_manager() -> ConfigManager:
    """Factory for ConfigManager."""
    return PydanticConfigManager()