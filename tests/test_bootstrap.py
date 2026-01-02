"""Tests for bootstrap protocols."""

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

from cytraco import bootstrap
from cytraco.model.config import Config
from tests import generators as generate

if TYPE_CHECKING:
    from cytraco.bootstrap import AppConfig, AppRunner


class MockConfigurable:
    """Mock implementation of Configurable for testing."""

    def __init__(self) -> None:
        """Initialize mock with default config."""
        self._config = Config(ftp=generate.ftp())

    def load_file(self, _path: Path) -> Config:
        """Mock load_file implementation."""
        return Config(ftp=generate.ftp(), device_address=generate.mac_address())

    def write_file(self, _path: Path, _config: Config) -> None:
        """Mock write_file implementation."""


class MockRunnable:
    """Mock implementation of Runnable for testing."""

    def __init__(self) -> None:
        """Initialize mock in non-started state."""
        self.started = False

    def start(self) -> None:
        """Mock start implementation."""
        self.started = True


def test_configurable_protocol_load_file() -> None:
    """Configurable implementations should load config from file."""
    configurable: AppConfig = MockConfigurable()
    config = configurable.load_file(Path("test.toml"))
    assert isinstance(config, Config)
    assert config.device_address is not None
    assert config.ftp is not None


def test_configurable_protocol_write_file() -> None:
    """Configurable implementations should write config to file."""
    configurable: AppConfig = MockConfigurable()
    config = generate.config()
    configurable.write_file(Path("test.toml"), config)


def test_runnable_protocol_start() -> None:
    """Runnable implementations should start correctly."""
    runnable: AppRunner = MockRunnable()
    runnable.start()
    assert runnable.started


def test_bootstrap_app_existing_config(tmp_path: Path) -> None:
    """bootstrap_app should return existing config without prompting."""
    config_path = tmp_path / "config.toml"
    existing_config = generate.config()

    mock_config_handler = MagicMock()
    mock_config_handler.load_file.return_value = existing_config

    mock_setup_ui = MagicMock()

    result = bootstrap.bootstrap_app(
        config_path,
        mock_config_handler,
        mock_setup_ui,
    )

    assert result == existing_config
    mock_config_handler.load_file.assert_called_once_with(config_path)
    mock_setup_ui.prompt_ftp.assert_not_called()
    mock_config_handler.write_file.assert_not_called()


def test_bootstrap_app_missing_config(tmp_path: Path) -> None:
    """bootstrap_app should prompt and save when config doesn't exist."""
    config_path = tmp_path / "config.toml"
    test_ftp = generate.ftp()

    mock_config_handler = MagicMock()
    mock_config_handler.load_file.side_effect = FileNotFoundError()

    mock_setup_ui = MagicMock()
    mock_setup_ui.prompt_ftp.return_value = test_ftp

    result = bootstrap.bootstrap_app(
        config_path,
        mock_config_handler,
        mock_setup_ui,
    )

    assert result.ftp == test_ftp
    assert result.device_address is None
    mock_setup_ui.prompt_ftp.assert_called_once()
    mock_config_handler.write_file.assert_called_once()

    # Verify the config written
    call_args = mock_config_handler.write_file.call_args
    assert call_args[0][0] == config_path
    assert call_args[0][1].ftp == test_ftp
