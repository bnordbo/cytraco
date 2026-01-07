"""Tests for bootstrap protocols."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

import cytraco.bootstrap as bts
import cytraco.config as cfg
import cytraco.trainer as trn
from cytraco.model import config as mcfg
from tests import generators as generate


class MockConfigurable:
    """Mock implementation of Configurable for testing."""

    def __init__(self) -> None:
        """Initialize mock with default config."""
        self._config = mcfg.Config(ftp=generate.ftp())

    def load_file(self, _path: Path) -> mcfg.Config:
        """Mock load_file implementation."""
        return mcfg.Config(ftp=generate.ftp(), device_address=generate.mac_address())

    def write_file(self, _path: Path, _config: mcfg.Config) -> None:
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
    configurable: bts.AppConfig = MockConfigurable()
    config = configurable.load_file(Path("test.toml"))
    assert isinstance(config, mcfg.Config)
    assert config.device_address is not None
    assert config.ftp is not None


def test_configurable_protocol_write_file() -> None:
    """Configurable implementations should write config to file."""
    configurable: bts.AppConfig = MockConfigurable()
    config = generate.config()
    configurable.write_file(Path("test.toml"), config)


def test_runnable_protocol_start() -> None:
    """Runnable implementations should start correctly."""
    runnable: bts.AppRunner = MockRunnable()
    runnable.start()
    assert runnable.started


@pytest.mark.asyncio
async def test_bootstrap_app_existing_config_connects(tmp_path: Path) -> None:
    """bootstrap_app returns config when configured trainer connects."""
    config_path = tmp_path / "config.toml"
    existing_config = generate.config()

    config_handler = cfg.TomlConfig()
    config_handler.write_file(config_path, existing_config)

    mock_setup_ui = MagicMock()
    mock_scanner = AsyncMock()
    mock_scanner.connect.return_value = True

    result = await bts.bootstrap_app(config_path, config_handler, mock_setup_ui, mock_scanner)

    assert result is not None
    assert isinstance(result, bts.BootstrapResult)
    assert result.config.ftp == existing_config.ftp
    assert result.config.device_address == existing_config.device_address
    assert result.demo_mode is False
    mock_setup_ui.prompt_ftp.assert_not_called()


@pytest.mark.asyncio
async def test_bootstrap_app_missing_config_selects_trainer(tmp_path: Path) -> None:
    """bootstrap_app prompts FTP and trainer selection when config missing."""
    config_path = tmp_path / "config.toml"
    test_ftp = generate.ftp()
    test_trainer = generate.trainer_info()

    config_handler = cfg.TomlConfig()

    mock_setup_ui = MagicMock()
    mock_setup_ui.prompt_ftp.return_value = test_ftp
    mock_setup_ui.prompt_trainer_selection.return_value = trn.TrainerSelected(trainer=test_trainer)

    mock_scanner = AsyncMock()
    mock_scanner.scan.return_value = [test_trainer]

    result = await bts.bootstrap_app(config_path, config_handler, mock_setup_ui, mock_scanner)

    assert result is not None
    assert result.config.ftp == test_ftp
    assert result.config.device_address == test_trainer.address
    assert result.demo_mode is False
    mock_setup_ui.prompt_ftp.assert_called_once()
    assert config_path.exists()


@pytest.mark.asyncio
async def test_bootstrap_app_user_exits_ftp(tmp_path: Path) -> None:
    """bootstrap_app returns None when user exits during FTP prompt."""
    config_path = tmp_path / "config.toml"

    config_handler = cfg.TomlConfig()

    mock_setup_ui = MagicMock()
    mock_setup_ui.prompt_ftp.return_value = None

    mock_scanner = AsyncMock()

    result = await bts.bootstrap_app(config_path, config_handler, mock_setup_ui, mock_scanner)

    assert result is None
    mock_setup_ui.prompt_ftp.assert_called_once()
    assert not config_path.exists()


@pytest.mark.asyncio
async def test_bootstrap_app_user_exits_trainer_selection(tmp_path: Path) -> None:
    """bootstrap_app returns None when user exits during trainer selection."""
    config_path = tmp_path / "config.toml"
    test_ftp = generate.ftp()

    config_handler = cfg.TomlConfig()

    mock_setup_ui = MagicMock()
    mock_setup_ui.prompt_ftp.return_value = test_ftp
    mock_setup_ui.prompt_trainer_selection.return_value = trn.UserAction.EXIT

    mock_scanner = AsyncMock()
    mock_scanner.scan.return_value = []

    result = await bts.bootstrap_app(config_path, config_handler, mock_setup_ui, mock_scanner)

    assert result is None


@pytest.mark.asyncio
async def test_bootstrap_app_demo_mode(tmp_path: Path) -> None:
    """bootstrap_app returns demo_mode=True when user chooses demo."""
    config_path = tmp_path / "config.toml"
    test_ftp = generate.ftp()

    config_handler = cfg.TomlConfig()

    mock_setup_ui = MagicMock()
    mock_setup_ui.prompt_ftp.return_value = test_ftp
    mock_setup_ui.prompt_trainer_selection.return_value = trn.UserAction.DEMO

    mock_scanner = AsyncMock()
    mock_scanner.scan.return_value = []

    result = await bts.bootstrap_app(config_path, config_handler, mock_setup_ui, mock_scanner)

    assert result is not None
    assert result.demo_mode is True
    assert result.config.ftp == test_ftp
    assert result.config.device_address is None


@pytest.mark.asyncio
async def test_bootstrap_app_connection_failed_scan(tmp_path: Path) -> None:
    """bootstrap_app scans when connection fails and user chooses scan."""
    config_path = tmp_path / "config.toml"
    existing_config = generate.config()
    new_trainer = generate.trainer_info()

    config_handler = cfg.TomlConfig()
    config_handler.write_file(config_path, existing_config)

    mock_setup_ui = MagicMock()
    mock_setup_ui.prompt_reconnect.return_value = trn.UserAction.SCAN
    mock_setup_ui.prompt_trainer_selection.return_value = trn.TrainerSelected(trainer=new_trainer)

    mock_scanner = AsyncMock()
    mock_scanner.connect.return_value = False
    mock_scanner.scan.return_value = [new_trainer]

    result = await bts.bootstrap_app(config_path, config_handler, mock_setup_ui, mock_scanner)

    assert result is not None
    assert result.config.device_address == new_trainer.address
    mock_setup_ui.prompt_reconnect.assert_called_once()
    mock_scanner.scan.assert_called_once()


@pytest.mark.asyncio
async def test_bootstrap_app_retry_then_success(tmp_path: Path) -> None:
    """bootstrap_app retries scan when user chooses retry."""
    config_path = tmp_path / "config.toml"
    test_ftp = generate.ftp()
    test_trainer = generate.trainer_info()

    config_handler = cfg.TomlConfig()

    mock_setup_ui = MagicMock()
    mock_setup_ui.prompt_ftp.return_value = test_ftp
    mock_setup_ui.prompt_trainer_selection.side_effect = [
        trn.UserAction.RETRY,
        trn.TrainerSelected(trainer=test_trainer),
    ]

    mock_scanner = AsyncMock()
    mock_scanner.scan.return_value = [test_trainer]

    result = await bts.bootstrap_app(config_path, config_handler, mock_setup_ui, mock_scanner)

    assert result is not None
    assert result.config.device_address == test_trainer.address
    # Two calls: first returns RETRY, second returns TrainerSelected
    assert mock_setup_ui.prompt_trainer_selection.call_count == mock_scanner.scan.call_count
