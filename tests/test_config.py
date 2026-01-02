"""Tests for configuration model."""

import stat
from pathlib import Path

import pytest

from cytraco import errors
from cytraco.config import TomlConfig
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


def test_load_valid_toml(tmp_path: Path) -> None:
    """TomlConfig should load valid TOML file."""
    config_path = tmp_path / "config.toml"
    expected_ftp = 300
    config_path.write_text(f'device_address = "AA:BB:CC:DD:EE:FF"\nftp = {expected_ftp}\n')

    toml_config = TomlConfig()
    config = toml_config.load_file(config_path)

    assert config.device_address == "AA:BB:CC:DD:EE:FF"
    assert config.ftp == expected_ftp


def test_load_missing_file(tmp_path: Path) -> None:
    """TomlConfig should raise ConfigError when file doesn't exist."""
    config_path = tmp_path / "nonexistent.toml"

    toml_config = TomlConfig()

    with pytest.raises(errors.ConfigError, match="Config file not found"):
        toml_config.load_file(config_path)


def test_load_malformed_toml(tmp_path: Path) -> None:
    """TomlConfig should raise ConfigError for malformed TOML."""
    config_path = tmp_path / "bad.toml"
    config_path.write_text("device_address = invalid toml content\n")

    toml_config = TomlConfig()

    with pytest.raises(errors.ConfigError, match="Invalid TOML"):
        toml_config.load_file(config_path)


def test_write_config_with_both_fields(tmp_path: Path) -> None:
    """TomlConfig should write config with both device_address and ftp."""
    config_path = tmp_path / "config.toml"
    config = generate.config()

    toml_config = TomlConfig()
    toml_config.write_file(config_path, config)

    assert config_path.exists()
    content = config_path.read_text()
    assert f'device_address = "{config.device_address}"' in content
    assert f"ftp = {config.ftp}" in content


def test_write_config_with_only_device_address(tmp_path: Path) -> None:
    """TomlConfig should write config with only device_address when ftp is None."""
    config_path = tmp_path / "config.toml"
    config = Config(device_address=generate.mac_address(), ftp=None)

    toml_config = TomlConfig()
    toml_config.write_file(config_path, config)

    assert config_path.exists()
    content = config_path.read_text()
    assert f'device_address = "{config.device_address}"' in content
    assert "ftp" not in content


def test_write_config_with_none_device_address(tmp_path: Path) -> None:
    """TomlConfig should raise ConfigError when device_address is None."""
    config_path = tmp_path / "config.toml"
    config = Config(device_address=None, ftp=generate.ftp())

    toml_config = TomlConfig()

    with pytest.raises(errors.ConfigError, match="Cannot write config without device_address"):
        toml_config.write_file(config_path, config)


def test_round_trip(tmp_path: Path) -> None:
    """TomlConfig should preserve config through write and read."""
    config_path = tmp_path / "config.toml"
    original_config = generate.config()

    toml_config = TomlConfig()
    toml_config.write_file(config_path, original_config)
    loaded_config = toml_config.load_file(config_path)

    assert loaded_config.device_address == original_config.device_address
    assert loaded_config.ftp == original_config.ftp


def test_parent_directory_creation(tmp_path: Path) -> None:
    """TomlConfig should create parent directories when writing."""
    config_path = tmp_path / "subdir" / "nested" / "config.toml"
    config = generate.config()

    toml_config = TomlConfig()
    toml_config.write_file(config_path, config)

    assert config_path.exists()
    assert config_path.parent.exists()


def test_permission_error(tmp_path: Path) -> None:
    """TomlConfig should raise ConfigError on permission denied."""
    config_dir = tmp_path / "readonly"
    config_dir.mkdir()
    config_path = config_dir / "config.toml"

    # Make directory read-only
    config_dir.chmod(stat.S_IRUSR | stat.S_IXUSR)

    toml_config = TomlConfig()
    config = generate.config()

    try:
        with pytest.raises(errors.ConfigError, match="Permission denied|Failed to write config"):
            toml_config.write_file(config_path, config)
    finally:
        # Restore permissions for cleanup
        config_dir.chmod(stat.S_IRWXU)
