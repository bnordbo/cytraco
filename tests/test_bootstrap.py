"""Tests for bootstrap protocols."""

from pathlib import Path
from typing import TYPE_CHECKING

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
