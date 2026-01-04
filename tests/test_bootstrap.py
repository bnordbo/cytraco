"""Tests for bootstrap protocols."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from cytraco.bootstrap import AppConfig, AppRunner, UserChoice, bootstrap_app
from cytraco.config import TomlConfig
from cytraco.model.config import Config
from tests import generators as generate


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


@pytest.mark.asyncio
async def test_bootstrap_app_existing_config(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """bootstrap_app should return existing config with trainer selection."""
    config_path = tmp_path / "config.toml"
    existing_config = generate.config()
    trainer = generate.trainer_info()
    trainer.address = existing_config.device_address

    # Use real TomlConfig, write actual file
    config_handler = TomlConfig()
    config_handler.write_file(config_path, existing_config)

    # Mock trainer functions
    mock_check_connection = AsyncMock(return_value=True)
    mock_scan = AsyncMock(return_value=[trainer])
    monkeypatch.setattr("cytraco.bootstrap.trn.check_connection", mock_check_connection)
    monkeypatch.setattr("cytraco.bootstrap.trn.scan_for_trainers", mock_scan)

    mock_setup_ui = MagicMock()
    result = await bootstrap_app(config_path, config_handler, mock_setup_ui)

    assert result is not None
    assert result.ftp == existing_config.ftp
    assert result.device_address == existing_config.device_address
    mock_setup_ui.prompt_ftp.assert_not_called()


@pytest.mark.asyncio
async def test_bootstrap_app_missing_config(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """bootstrap_app should prompt and save when config doesn't exist."""
    config_path = tmp_path / "config.toml"
    test_ftp = generate.ftp()
    trainer = generate.trainer_info()

    # Use real TomlConfig, no mocking
    config_handler = TomlConfig()

    # Mock trainer functions
    mock_scan = AsyncMock(return_value=[trainer])
    monkeypatch.setattr("cytraco.bootstrap.trn.scan_for_trainers", mock_scan)

    mock_setup_ui = MagicMock()
    mock_setup_ui.prompt_ftp.return_value = test_ftp
    mock_setup_ui.prompt_single_trainer.return_value = UserChoice.CONTINUE
    result = await bootstrap_app(config_path, config_handler, mock_setup_ui)

    assert result is not None
    assert result.ftp == test_ftp
    assert result.device_address == trainer.address
    mock_setup_ui.prompt_ftp.assert_called_once()
    assert config_path.exists()


@pytest.mark.asyncio
async def test_bootstrap_app_user_exits(tmp_path: Path) -> None:
    """bootstrap_app should return None when user exits during setup."""
    config_path = tmp_path / "config.toml"

    config_handler = TomlConfig()

    mock_setup_ui = MagicMock()
    mock_setup_ui.prompt_ftp.return_value = None
    result = await bootstrap_app(config_path, config_handler, mock_setup_ui)

    assert result is None
    mock_setup_ui.prompt_ftp.assert_called_once()

    # Verify no config was written
    assert not config_path.exists()
