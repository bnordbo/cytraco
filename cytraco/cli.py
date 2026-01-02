"""CLI entry point for Cytraco application."""

import sys
from pathlib import Path

from cytraco import bootstrap, errors
from cytraco.config import TomlConfig
from cytraco.ui.setup import TerminalSetup


def app() -> None:
    """Run the main application.

    Bootstraps the application by ensuring configuration exists,
    prompting user for FTP if needed.
    """
    config_path = Path.home() / ".config" / "cytraco" / "config.toml"

    config_handler = TomlConfig()
    setup_ui = TerminalSetup()

    try:
        config = bootstrap.bootstrap_app(
            config_path,
            config_handler,
            setup_ui,
        )
        print(f"\nConfiguration loaded. FTP: {config.ftp}W")

        # TODO: Detect trainer (next TODO - trainer selection UI)
        # TODO: Start workout (when workout module is ready)
        print("Setup complete! (Trainer detection and workout not yet implemented)")

    except errors.ConfigError as e:
        print(f"\nConfiguration error: {e}", file=sys.stderr)
        sys.exit(1)
    except errors.DeviceError as e:
        print(f"\nDevice error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(130)
