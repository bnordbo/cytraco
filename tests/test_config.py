"""Tests for configuration model."""

from cytraco.model.config import Config


def test_config_with_defaults() -> None:
    """Config should initialize with None defaults."""
    config = Config()
    assert config.device_address is None
    assert config.ftp is None


def test_config_with_device_address() -> None:
    """Config should store device address."""
    address = "AA:BB:CC:DD:EE:FF"
    config = Config(device_address=address)
    assert config.device_address == address
    assert config.ftp is None


def test_config_with_ftp() -> None:
    """Config should store FTP value."""
    ftp = 300
    config = Config(ftp=ftp)
    assert config.device_address is None
    assert config.ftp == ftp


def test_config_with_all_values() -> None:
    """Config should store both device address and FTP."""
    address = "11:22:33:44:55:66"
    ftp = 250
    config = Config(device_address=address, ftp=ftp)
    assert config.device_address == address
    assert config.ftp == ftp
