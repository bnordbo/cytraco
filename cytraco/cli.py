"""CLI entry point for Cytraco application."""

import asyncio
import sys
from pathlib import Path

import cytraco.bootstrap as bts
import cytraco.config as cfg
import cytraco.ui.setup as sup
from cytraco import errors


def app() -> None:
    """Run the main application.

    Bootstraps the application by ensuring configuration exists,
    prompting user for FTP and trainer selection if needed.
    """
    config_path = Path.home() / ".config" / "cytraco" / "config.toml"

    config_handler = cfg.TomlConfig()
    setup_ui = sup.TerminalSetup()

    try:
        config = asyncio.run(bts.bootstrap_app(config_path, config_handler, setup_ui))
        if config is None:
            print("\nSetup cancelled by user")
            sys.exit(0)

        print(f"\nConfiguration loaded. FTP: {config.ftp}W")
        if config.device_address:
            print(f"Trainer: {config.device_address}")
        print("Setup complete! (Workout execution not yet implemented)")

    except errors.ConfigError as e:
        print(f"\nConfiguration error: {e}", file=sys.stderr)
        sys.exit(1)
    except errors.DeviceError as e:
        print(f"\nDevice error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(130)
