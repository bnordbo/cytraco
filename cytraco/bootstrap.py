"""Bootstrap protocols for application lifecycle and configuration. Alias: bts.

This module defines protocols for the bootstrap use-case layer. These protocols
are implemented by higher layers following the dependency inversion principle.

"""

from enum import Enum
from pathlib import Path
from typing import Protocol

from cytraco import trainer as trn
from cytraco.model.config import Config


class UserChoice(Enum):
    """User input choices with keyboard shortcuts."""

    CONTINUE = ("c", "continue")
    RETRY = ("r", "retry")
    SCAN = ("s", "scan")
    EXIT = ("e", "exit")

    def __init__(self, shortcut: str, description: str) -> None:
        """Initialize choice with shortcut and description."""
        self.shortcut = shortcut
        self.description = description

    @classmethod
    def from_input(cls, value: str) -> "UserChoice | None":
        """Parse user input to UserChoice."""
        value_lower = value.lower().strip()
        for choice in cls:
            if value_lower == choice.shortcut:
                return choice
        return None


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

    def prompt_trainer_selection(
        self,
        trainers: list[trn.TrainerInfo],
    ) -> trn.TrainerInfo | None:
        """Prompt user to select from multiple trainers.

        Args:
            trainers: List of discovered trainers (must be non-empty).

        Returns:
            Selected trainer, or None if user exits.
        """
        ...

    def prompt_single_trainer(self, trainer: trn.TrainerInfo) -> UserChoice | None:
        """Prompt user to confirm single discovered trainer.

        Args:
            trainer: The single discovered trainer.

        Returns:
            UserChoice.CONTINUE to continue, UserChoice.RETRY to retry scan,
            or None if user exits.
        """
        ...

    def prompt_no_trainers(self) -> UserChoice | None:
        """Prompt user when no trainers found.

        Returns:
            UserChoice.RETRY to retry scan, or None if user exits.
        """
        ...

    def prompt_connection_failed(self, address: str) -> UserChoice | None:
        """Prompt user when configured trainer is unreachable.

        Args:
            address: Device address of configured but unreachable trainer.

        Returns:
            UserChoice (RETRY, SCAN), or None if user exits.
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


async def bootstrap_app(
    config_path: Path,
    config_handler: AppConfig,
    setup_ui: SetupUI,
) -> Config | None:
    """Bootstrap Cytraco: ensure config exists.

    Loads existing configuration or prompts user for required values.
    Tests configured trainer connection or scans for trainers as needed.
    Saves configuration to disk.

    Args:
        config_path: Path to configuration file.
        config_handler: AppConfig implementation for loading/saving config.
        setup_ui: SetupUI implementation for prompting user.

    Returns:
        Complete configuration, or None if user exits.
    """
    # Load or create config with FTP
    if config_path.exists():
        config = config_handler.load_file(config_path)
    else:
        ftp_value = setup_ui.prompt_ftp()
        if ftp_value is None:
            return None
        config = Config(ftp=ftp_value)

    # Test configured trainer or scan for trainers
    selected_trainer = await _select_trainer(config, setup_ui)
    if selected_trainer is None:
        return None

    # Update and save config with trainer
    config.device_address = selected_trainer.address
    config_handler.write_file(config_path, config)

    return config


async def _test_configured_trainer(address: str) -> trn.TrainerInfo | None:
    """Test connection to configured trainer and return TrainerInfo if reachable.

    Args:
        address: Device address of configured trainer.

    Returns:
        TrainerInfo if connection succeeds and trainer found in scan, None otherwise.
    """
    if not await trn.check_connection(address):
        return None
    trainers = await trn.scan_for_trainers()
    for trainer in trainers:
        if trainer.address == address:
            return trainer
    return None


async def _handle_unreachable_trainer(
    address: str,
    setup_ui: SetupUI,
) -> trn.TrainerInfo | None:
    """Handle unreachable configured trainer with retry/scan options.

    Args:
        address: Device address of configured but unreachable trainer.
        setup_ui: SetupUI implementation for prompting user.

    Returns:
        TrainerInfo if retry succeeds or user chooses scan, None if user exits.
        Returns sentinel value "scan" to indicate user chose to scan.
    """
    while True:
        choice = setup_ui.prompt_connection_failed(address)
        if choice is None:
            return None
        if choice == UserChoice.RETRY:
            trainer = await _test_configured_trainer(address)
            if trainer is not None:
                return trainer
            continue
        if choice == UserChoice.SCAN:
            return "scan"  # Sentinel to continue to scan flow
        return None


async def _scan_and_select_trainer(setup_ui: SetupUI) -> trn.TrainerInfo | None:
    """Scan for trainers and handle user selection.

    Args:
        setup_ui: SetupUI implementation for prompting user.

    Returns:
        Selected TrainerInfo, or None if user exits.
    """
    while True:
        trainers = await trn.scan_for_trainers()

        if len(trainers) == 0:
            choice = setup_ui.prompt_no_trainers()
            if choice is None or choice != UserChoice.RETRY:
                return None
            continue

        if len(trainers) == 1:
            choice = setup_ui.prompt_single_trainer(trainers[0])
            if choice is None:
                return None
            if choice == UserChoice.CONTINUE:
                return trainers[0]
            continue

        # Multiple trainers
        selected = setup_ui.prompt_trainer_selection(trainers)
        if selected is None:
            return None
        return selected


async def _select_trainer(config: Config, setup_ui: SetupUI) -> trn.TrainerInfo | None:
    """Select trainer through connection test or scan.

    Args:
        config: Current configuration (may have device_address set).
        setup_ui: SetupUI implementation for prompting user.

    Returns:
        Selected trainer, or None if user exits.
    """
    # Test configured trainer if present
    if config.device_address is not None:
        trainer = await _test_configured_trainer(config.device_address)
        if trainer is not None:
            return trainer

        # Trainer unreachable, prompt user
        result = await _handle_unreachable_trainer(config.device_address, setup_ui)
        if result is None:
            return None
        if result != "scan":
            return result

    # Scan for trainers (either no trainer configured or user chose scan)
    return await _scan_and_select_trainer(setup_ui)
