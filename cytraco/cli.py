"""CLI entry point for Cytraco application."""

import argparse
import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path

import cytraco.bootstrap as bts
import cytraco.config as cfg
import cytraco.trainer as trn
import cytraco.ui.setup as sup
from cytraco import errors


@dataclass
class CliArgs:
    """Parsed CLI arguments."""

    demo: bool


def parse_args(args: list[str] | None = None) -> CliArgs:
    """Parse command line arguments.

    Args:
        args: Arguments to parse. If None, uses sys.argv.

    Returns:
        Parsed arguments as CliArgs dataclass.
    """
    parser = argparse.ArgumentParser(
        prog="cytraco",
        description="Cycling trainer controller for automated interval workouts",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode without connecting to a trainer",
    )
    parsed = parser.parse_args(args)
    return CliArgs(demo=parsed.demo)


async def _run_app() -> None:
    """Run the main application asynchronously."""
    args = parse_args()
    config_path = Path.home() / ".config" / "cytraco" / "config.toml"
    config_handler = cfg.TomlConfig()

    if args.demo:
        result = await bts.bootstrap_demo_mode(config_path, config_handler)
    else:
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
