"""Configuration file operations."""

import tomllib
from pathlib import Path

from cytraco import errors
from cytraco.model.config import Config


class TomlConfig:
    """TOML-based configuration persistence."""

    def load_file(self, path: Path) -> Config:
        """Load configuration from TOML file.

        Args:
            path: Path to the configuration file.

        Returns:
            Config object populated with values from the file.

        Raises:
            ConfigError: If the file doesn't exist, is malformed, or cannot be read.
        """
        try:
            with path.open("rb") as f:
                data = tomllib.load(f)
            return Config(
                device_address=data.get("device_address"),
                ftp=data.get("ftp"),
            )
        except FileNotFoundError as e:
            raise errors.ConfigError(f"Config file not found: {path}") from e
        except tomllib.TOMLDecodeError as e:
            raise errors.ConfigError(f"Invalid TOML in {path}: {e}") from e
        except Exception as e:
            raise errors.ConfigError(f"Failed to load config: {e}") from e

    def write_file(self, path: Path, config: Config) -> None:
        """Write configuration to TOML file.

        Args:
            path: Path where configuration will be written.
            config: Configuration object to write.

        Raises:
            ConfigError: If the file cannot be written or config is invalid.
        """
        if config.device_address is None:
            raise errors.ConfigError("Cannot write config without device_address")

        try:
            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)

            # Build TOML content manually
            lines = []
            lines.append(f'device_address = "{config.device_address}"')
            if config.ftp is not None:
                lines.append(f"ftp = {config.ftp}")

            content = "\n".join(lines)
            if content:
                content += "\n"  # Trailing newline

            path.write_text(content)
        except PermissionError as e:
            raise errors.ConfigError(f"Permission denied writing {path}") from e
        except Exception as e:
            raise errors.ConfigError(f"Failed to write config: {e}") from e
