"""Configuration file operations. Alias: cfg."""

import tomllib
from pathlib import Path

import tomli_w

from cytraco import errors
from cytraco.model import config as cfg


class TomlConfig:
    """TOML-based configuration persistence."""

    def load_file(self, path: Path) -> cfg.Config:
        """Load configuration from TOML file.

        Args:
            path: Path to the configuration file.

        Returns:
            Config object populated with values from the file.

        Raises:
            FileNotFoundError: If the configuration file doesn't exist.
            ConfigError: If the file is malformed or cannot be read.
        """
        try:
            with path.open("rb") as f:
                data = tomllib.load(f)
            return cfg.Config(
                ftp=data["ftp"],
                device_address=data.get("device_address"),
            )
        except tomllib.TOMLDecodeError as e:
            raise errors.ConfigError(f"Invalid TOML in {path}: {e}") from e
        except (KeyError, TypeError) as e:
            raise errors.ConfigError(f"Invalid config structure in {path}: {e}") from e

    def write_file(self, path: Path, config: cfg.Config) -> None:
        """Write configuration to TOML file.

        Args:
            path: Path where configuration will be written.
            config: Configuration object to write.

        Raises:
            ConfigError: If the file cannot be written or config is invalid.
        """
        try:
            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)

            # Build data dict, skip None values
            data: dict[str, str | int] = {"ftp": config.ftp}
            if config.device_address is not None:
                data["device_address"] = config.device_address

            with path.open("wb") as f:
                tomli_w.dump(data, f)
        except PermissionError as e:
            raise errors.ConfigError(f"Permission denied writing {path}") from e
        except Exception as e:
            raise errors.ConfigError(f"Failed to write config: {e}") from e
