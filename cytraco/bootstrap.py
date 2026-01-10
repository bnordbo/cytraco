"""Bootstrap protocols for application lifecycle and configuration. Alias: bts.

This module defines protocols for the bootstrap use-case layer. These protocols
are implemented by higher layers following the dependency inversion principle.

"""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import cytraco.model.config as cfg
import cytraco.trainer as trn

DEFAULT_FTP = 200


@dataclass
class BootstrapResult:
    """Result of bootstrap process."""

    config: cfg.Config
    demo_mode: bool = False


class SetupUI(Protocol):
    """Protocol for setup user interface.

    Classes implementing this protocol can prompt users for
    configuration values during initial setup.
    """

    def prompt_ftp(self) -> int | None:
        """Prompt user for FTP in watts.

        Returns:
            FTP value entered by user (positive integer), or None if user exits.
        """
        ...

    def prompt_reconnect(self, address: str) -> trn.TrainerResult:
        """Ask user how to proceed when configured trainer is unreachable.

        Args:
            address: The BLE address of the unreachable trainer.

        Returns:
            User's choice: RETRY, SCAN, EXIT, or DEMO.
        """
        ...

    def prompt_trainer_selection(self, trainers: list[trn.TrainerInfo]) -> trn.TrainerResult:
        """Show discovered trainers and let user select one.

        Args:
            trainers: List of discovered trainers (may be empty).

        Returns:
            TrainerSelected with chosen trainer, or UserAction (RETRY, EXIT, DEMO).
        """
        ...


class AppConfig(Protocol):
    """Protocol for configuration management.

    Classes implementing this protocol can load and persist configuration
    to/from files.
    """

    def load_file(self, path: Path) -> cfg.Config:
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

    def write_file(self, path: Path, config: cfg.Config) -> None:
        """Write configuration to a file.

        Args:
            path: Path where configuration will be written.
            config: Configuration object to write.

        Raises:
            ConfigError: If the file cannot be written or config is invalid.
        """
        ...


class TrainerScanner(Protocol):
    """Protocol for trainer discovery and connection.

    Classes implementing this protocol can scan for BLE trainers
    and attempt connections.
    """

    async def scan(self) -> list[trn.TrainerInfo]:
        """Scan for available trainers.

        Returns:
            List of discovered trainers.

        Raises:
            DeviceError: If BLE scanning fails.
        """
        ...

    async def connect(self, address: str) -> bool:
        """Attempt to connect to a trainer.

        Args:
            address: BLE address of the trainer.

        Returns:
            True if connection successful, False otherwise.
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


async def bootstrap_app(
    config_path: Path,
    config_handler: AppConfig,
    setup_ui: SetupUI,
    trainer_scanner: TrainerScanner,
) -> BootstrapResult | None:
    """Bootstrap Cytraco: ensure config exists and trainer is selected.

    Loads existing configuration or prompts user for required values
    (like FTP) if config doesn't exist. Handles trainer detection and
    selection. Saves the configuration to disk.

    Args:
        config_path: Path to configuration file.
        config_handler: AppConfig implementation for loading/saving config.
        setup_ui: SetupUI implementation for prompting user.
        trainer_scanner: TrainerScanner implementation for BLE operations.

    Returns:
        BootstrapResult with config and demo_mode flag, or None if user exits.
    """
    # Load existing config or prompt for FTP
    if config_path.exists():
        config = config_handler.load_file(config_path)
    else:
        if (ftp_value := setup_ui.prompt_ftp()) is None:
            return None
        config = cfg.Config(ftp=ftp_value)

    # Handle trainer selection
    while True:
        if config.device_address:
            # Try to connect to configured trainer
            if await trainer_scanner.connect(config.device_address):
                config_handler.write_file(config_path, config)
                return BootstrapResult(config=config, demo_mode=False)
            # Connection failed, ask user what to do
            result = setup_ui.prompt_reconnect(config.device_address)
        else:
            # No trainer configured, scan for trainers
            trainers = await trainer_scanner.scan()
            result = setup_ui.prompt_trainer_selection(trainers)

        # Handle user's choice
        if isinstance(result, trn.TrainerSelected):
            config.device_address = result.trainer.address
            config_handler.write_file(config_path, config)
            return BootstrapResult(config=config, demo_mode=False)

        if result == trn.UserAction.EXIT:
            return None

        if result == trn.UserAction.DEMO:
            config_handler.write_file(config_path, config)
            return BootstrapResult(config=config, demo_mode=True)

        if result == trn.UserAction.SCAN:
            config.device_address = None  # Clear to trigger scan on next iteration

        # RETRY continues the loop


async def bootstrap_demo_mode(
    config_path: Path,
    config_handler: AppConfig,
    default_ftp: int = DEFAULT_FTP,
) -> BootstrapResult:
    """Bootstrap in demo mode, bypassing trainer selection.

    Loads existing config or creates one with default FTP.
    Always returns demo_mode=True. Useful for testing and development
    when no physical trainer is available.

    Args:
        config_path: Path to configuration file.
        config_handler: AppConfig implementation for loading/saving config.
        default_ftp: Default FTP to use if no config exists (default: DEFAULT_FTP).

    Returns:
        BootstrapResult with config and demo_mode=True.

    Raises:
        ConfigError: If config file exists but cannot be loaded.
    """
    if config_path.exists():
        config = config_handler.load_file(config_path)
    else:
        config = cfg.Config(ftp=default_ftp)
        config_handler.write_file(config_path, config)

    return BootstrapResult(config=config, demo_mode=True)
