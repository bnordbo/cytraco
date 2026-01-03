"""Bootstrap protocols for application lifecycle and configuration.

This module defines protocols for the bootstrap use-case layer. These protocols
are implemented by higher layers following the dependency inversion principle.

"""

from pathlib import Path
from typing import Protocol

from cytraco.model.config import Config


class SetupUI(Protocol):
    """Protocol for setup user interface.

    Classes implementing this protocol can prompt users for
    configuration values during initial setup.
    """

    def prompt_ftp(self) -> int:
        """Prompt user for FTP in watts.

        Returns:
            FTP value entered by user (positive integer).

        Raises:
            ConfigError: If user exits or input fails.
        """
        ...


class AppConfig(Protocol):
    """Protocol for configuration management.

    Classes implementing this protocol can load and persist configuration
    to/from files.
    """

    def load_file(self, path: Path) -> Config:
        """Load configuration from file.

        Args:
            path: Path to the configuration file.

        Returns:
            Config object populated with values from the file.

        Raises:
            FileNotFoundError: If the configuration file doesn't exist.
            ValueError: If the file is malformed or contains invalid values.
        """
        ...

    def write_file(self, path: Path, config: Config) -> None:
        """Write configuration to a file.

        Args:
            path: Path where configuration will be written.
            config: Configuration object to write.

        Raises:
            ConfigError: If the file cannot be written or config is invalid.
        """
        ...


class AppRunner(Protocol):
    """Protocol for runnable application components.

    Classes implementing this protocol can be started and will run until
    completion or interruption. This is typically used for the main
    application lifecycle.
    """

    def start(self) -> None:
        """Start the runnable component.

        This method may block until the component completes or is interrupted.
        Implementations should handle cleanup and graceful shutdown.

        Raises:
            AppRunnerError: If the component cannot be started or encounters
                a fatal error during execution.
        """
        ...


def bootstrap_app(
    config_path: Path,
    config_handler: AppConfig,
    setup_ui: SetupUI,
) -> Config:
    """Bootstrap Cytraco: ensure config exists, prompting user if needed.

    Loads existing configuration or prompts user for required values
    (like FTP) if config doesn't exist. Saves the configuration to disk.

    Args:
        config_path: Path to configuration file.
        config_handler: AppConfig implementation for loading/saving config.
        setup_ui: SetupUI implementation for prompting user.

    Returns:
        Complete configuration.

    Raises:
        ConfigError: If setup fails or user exits.
    """
    try:
        return config_handler.load_file(config_path)
    except FileNotFoundError:
        pass

    ftp_value = setup_ui.prompt_ftp()
    config = Config(ftp=ftp_value)
    config_handler.write_file(config_path, config)

    return config
