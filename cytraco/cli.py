"""CLI entry point for Cytraco application."""

import asyncio
import sys
from pathlib import Path

import cytraco.bootstrap as bts
import cytraco.config as cfg
import cytraco.trainer as trn
import cytraco.ui.setup as sup
from cytraco import errors


async def _run_app() -> None:
    """Run the main application asynchronously."""
    config_path = Path.home() / ".config" / "cytraco" / "config.toml"

    config_handler = cfg.TomlConfig()
    setup_ui = sup.TerminalSetup()
    trainer_scanner = trn.BleakTrainerScanner()

    result = await bts.bootstrap_app(config_path, config_handler, setup_ui, trainer_scanner)
    if result is None:
        print("\nSetup cancelled by user")
        sys.exit(0)

    print(f"\nConfiguration loaded. FTP: {result.config.ftp}W")
    if result.demo_mode:
        print("Running in demo mode (no trainer connected)")
    else:
        print(f"Trainer: {result.config.device_address}")
    print("Setup complete! (Workout not yet implemented)")


def app() -> None:
    """Run the main application.

    Bootstraps the application by ensuring configuration exists,
    prompting user for FTP and trainer selection if needed.
    """
    try:
        asyncio.run(_run_app())
    except errors.ConfigError as e:
        print(f"\nConfiguration error: {e}", file=sys.stderr)
        sys.exit(1)
    except errors.DeviceError as e:
        print(f"\nDevice error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(130)
