"""Bootstrap protocols for application lifecycle and configuration. Alias: bts.

This module defines protocols for the bootstrap use-case layer. These protocols
are implemented by higher layers following the dependency inversion principle.

"""

from pathlib import Path
from typing import Protocol

from cytraco import trainer as trn
from cytraco.model.config import Config


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

    async def prompt_trainer_selection(
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

    async def prompt_single_trainer(self, trainer: trn.TrainerInfo) -> bool | None:
        """Prompt user to confirm single discovered trainer.

        Args:
            trainer: The single discovered trainer.

        Returns:
            True to continue, False to retry scan, None to exit.
        """
        ...

    async def prompt_no_trainers(self) -> bool | None:
        """Prompt user when no trainers found.

        Returns:
            True to retry scan, None to exit.
        """
        ...

    async def prompt_connection_failed(self, address: str) -> str | None:
        """Prompt user when configured trainer is unreachable.

        Args:
            address: Device address of configured but unreachable trainer.

        Returns:
            'retry' to retry connection, 'scan' to scan for trainers, None to exit.
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
    """Bootstrap Cytraco: ensure config exists with FTP and trainer.

    Loads existing configuration or prompts user for required values.
    Tests configured trainer connection or scans for trainers as needed.
    Saves complete configuration with both FTP and trainer to disk.

    Args:
        config_path: Path to configuration file.
        config_handler: AppConfig implementation for loading/saving config.
        setup_ui: SetupUI implementation for prompting user.

    Returns:
        Complete configuration with FTP and trainer, or None if user exits.
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


async def _select_trainer(config: Config, setup_ui: SetupUI) -> trn.TrainerInfo | None:  # noqa: C901, PLR0911, PLR0912
    """Select trainer through connection test or scan.

    Args:
        config: Current configuration (may have device_address set).
        setup_ui: SetupUI implementation for prompting user.

    Returns:
        Selected trainer, or None if user exits.
    """
    # Test configured trainer if present
    if config.device_address is not None:
        if await trn.check_connection(config.device_address):
            # Connection successful, find trainer info from scan
            trainers = await trn.scan_for_trainers()
            for trainer in trainers:
                if trainer.address == config.device_address:
                    return trainer
            # Address configured but not found in scan, treat as unreachable

        # Configured trainer unreachable, prompt user
        while True:
            choice = await setup_ui.prompt_connection_failed(config.device_address)
            if choice is None:
                return None
            if choice == "retry":
                if await trn.check_connection(config.device_address):
                    # Find trainer info from scan
                    trainers = await trn.scan_for_trainers()
                    for trainer in trainers:
                        if trainer.address == config.device_address:
                            return trainer
                continue
            if choice == "scan":
                break

    # Scan for trainers
    while True:
        trainers = await trn.scan_for_trainers()

        if len(trainers) == 0:
            retry = await setup_ui.prompt_no_trainers()
            if retry is None:
                return None
            continue

        if len(trainers) == 1:
            choice = await setup_ui.prompt_single_trainer(trainers[0])
            if choice is None:
                return None
            if choice is True:
                return trainers[0]
            continue

        # Multiple trainers
        selected = await setup_ui.prompt_trainer_selection(trainers)
        if selected is None:
            return None
        return selected
