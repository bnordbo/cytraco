"""Tests for configuration model."""

from cytraco.model.config import Config
from tests import generators as generate


def test_config_with_defaults() -> None:
    """Config should initialize with None defaults."""
    config = Config()
    assert config.device_address is None
    assert config.ftp is None


def test_config_with_device_address() -> None:
    """Config should store device address."""
    address = generate.mac_address()
    config = Config(device_address=address)
    assert config.device_address == address
    assert config.ftp is None


def test_config_with_ftp() -> None:
    """Config should store FTP value."""
    ftp = generate.ftp()
    config = Config(ftp=ftp)
    assert config.device_address is None
    assert config.ftp == ftp


def test_config_with_all_values() -> None:
    """Config should store both device address and FTP."""
    address = generate.mac_address()
    ftp = generate.ftp()
    config = Config(device_address=address, ftp=ftp)
    assert config.device_address == address
    assert config.ftp == ftp
