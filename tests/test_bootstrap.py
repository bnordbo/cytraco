"""Tests for bootstrap protocols."""

from pathlib import Path

from cytraco.bootstrap import AppConfig, AppRunner
from cytraco.model.config import Config
from tests import generators as generate


class MockConfigurable:
    """Mock implementation of Configurable for testing."""

    def __init__(self) -> None:
        self._config = Config()

    def load_file(self, path: Path) -> Config:
        """Mock load_file implementation."""
        return Config(device_address=generate.mac_address(), ftp=generate.ftp())

    def write_file(self, path: Path) -> None:
        """Mock write_file implementation."""
        pass


class MockRunnable:
    """Mock implementation of Runnable for testing."""

    def __init__(self) -> None:
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
    configurable.write_file(Path("test.toml"))


def test_runnable_protocol_start() -> None:
    """Runnable implementations should start correctly."""
    runnable: AppRunner = MockRunnable()
    runnable.start()
    assert runnable.started
