"""Bootstrap protocols for application lifecycle and configuration.

This module defines protocols for the bootstrap use-case layer. These protocols
are implemented by higher layers following the dependency inversion principle.

"""

from pathlib import Path
from typing import Protocol

from cytraco.model.config import Config


class Configurable(Protocol):
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

    def write_file(self, path: Path) -> None:
        """Write configuration to a file.

        Args:
            path: Path where configuration will be written.

        Raises:
            PermissionError: If the file cannot be written.
            ValueError: If the configuration contains invalid values.
        """
        ...


class Runnable(Protocol):
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
            RuntimeError: If the component cannot be started or encounters
                a fatal error during execution.
        """
        ...
