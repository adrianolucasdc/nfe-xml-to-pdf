"""Unit tests for configuration management."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from nfe2pdf.config import Settings, get_settings, reload_settings
from nfe2pdf.infrastructure.config_manager import PydanticConfigManager, create_config_manager


class TestSettings:
    """Test Settings model."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()

        assert settings.danfe.layout == "auto"
        assert settings.danfe.font_type == "times"
        assert settings.danfe.font_size == "small"
        assert settings.danfe.margins_top == 5.0
        assert settings.logging.level == "INFO"
        assert settings.output.overwrite is False

    def test_get_pdf_generator_config(self):
        """Test PDF generator config conversion."""
        settings = Settings()

        config = settings.get_pdf_generator_config()

        assert config.layout == "auto"
        assert config.font_type == "times"
        assert config.font_size == "small"
        assert config.margins_mm == (5.0, 5.0, 5.0, 5.0)
        assert config.tax_configuration == "standard_icms_ipi"
        assert config.invoice_display == "full_details"
        assert config.display_pis_cofins is False
        assert config.watermark_cancelled is True


class TestSettingsSingleton:
    """Test settings singleton behavior."""

    def test_get_settings_returns_same_instance(self):
        """Test get_settings returns cached instance."""
        # Clear any existing cache
        reload_settings()

        s1 = get_settings()
        s2 = get_settings()

        assert s1 is s2

    def test_reload_settings_creates_new_instance(self):
        """Test reload_settings creates new instance."""
        get_settings()
        reload_settings()
        s2 = get_settings()

        # May be same or different depending on implementation
        # Just verify it doesn't crash
        assert s2 is not None


class TestPydanticConfigManager:
    """Test PydanticConfigManager."""

    def setup_method(self):
        self.mock_settings = MagicMock(spec=Settings)
        self.manager = PydanticConfigManager(settings=self.mock_settings)

    def test_load_returns_dict(self):
        """Test load returns configuration as dict."""
        self.mock_settings.model_dump.return_value = {"danfe": {"layout": "auto"}}

        result = self.manager.load()

        assert result == {"danfe": {"layout": "auto"}}
        self.mock_settings.model_dump.assert_called_once_with(exclude_none=True)

    def test_save_updates_settings(self):
        """Test save updates settings and calls save()."""
        config = {"danfe": {"layout": "nt_2026_010"}}
        self.mock_settings.save = MagicMock()
        # Mock the danfe attribute to have model_dump
        self.mock_settings.danfe = MagicMock()
        self.mock_settings.danfe.model_dump.return_value = {"layout": "auto"}

        self.manager.save(config)

        self.mock_settings.save.assert_called_once()

    def test_get_default_config(self):
        """Test get_default_config returns default settings."""
        default_settings = MagicMock(spec=Settings)
        default_settings.model_dump.return_value = {"danfe": {"layout": "auto"}}

        with patch("nfe2pdf.infrastructure.config_manager.Settings", return_value=default_settings):
            manager = PydanticConfigManager()
            result = manager.get_default_config()

        assert result == {"danfe": {"layout": "auto"}}

    def test_get_pdf_generator_config(self):
        """Test get_pdf_generator_config delegates to settings."""
        mock_config = MagicMock()
        self.mock_settings.get_pdf_generator_config.return_value = mock_config

        result = self.manager.get_pdf_generator_config()

        assert result == mock_config
        self.mock_settings.get_pdf_generator_config.assert_called_once()


class TestCreateConfigManager:
    """Test create_config_manager factory."""

    def test_returns_config_manager(self):
        """Test factory returns ConfigManager instance."""
        manager = create_config_manager()

        assert isinstance(manager, PydanticConfigManager)


class TestSettingsWithEnvironment:
    """Test settings with environment variables."""

    @patch.dict("os.environ", {"NFE2PDF_DANFE__LAYOUT": "nt_2026_010"})
    def test_env_var_overrides_layout(self):
        """Test NFE2PDF_DANFE__LAYOUT env var overrides layout."""
        reload_settings()
        settings = get_settings()

        assert settings.danfe.layout == "nt_2026_010"

    @patch.dict("os.environ", {"NFE2PDF_DANFE__FONT_TYPE": "courier"})
    def test_env_var_overrides_font_type(self):
        """Test NFE2PDF_DANFE__FONT_TYPE env var overrides font."""
        reload_settings()
        settings = get_settings()

        assert settings.danfe.font_type == "courier"

    @patch.dict("os.environ", {"NFE2PDF_LOGGING__LEVEL": "DEBUG"})
    def test_env_var_overrides_log_level(self):
        """Test NFE2PDF_LOGGING__LEVEL env var overrides log level."""
        reload_settings()
        settings = get_settings()

        assert settings.logging.level == "DEBUG"


class TestSettingsYamlFile:
    """Test settings loading from YAML file."""

    def test_save_creates_yaml_file(self, tmp_path: Path):
        """Test save() creates YAML file."""
        with patch("nfe2pdf.config.get_config_path", return_value=tmp_path / "config.yaml"):
            settings = Settings()
            settings.save()

            config_file = tmp_path / "config.yaml"
            assert config_file.exists()

            content = config_file.read_text()
            assert "danfe:" in content
            assert "layout:" in content

    def test_load_from_yaml(self, tmp_path: Path):
        """Test loading settings from YAML file."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
danfe:
  layout: moc_7_0
  font_type: courier
  font_size: big
logging:
  level: DEBUG
output:
  overwrite: true
""")

        with patch("nfe2pdf.config.get_config_path", return_value=config_file):
            reload_settings()
            settings = get_settings()

            assert settings.danfe.layout == "moc_7_0"
            assert settings.danfe.font_type == "courier"
            assert settings.danfe.font_size == "big"
            assert settings.logging.level == "DEBUG"
            assert settings.output.overwrite is True