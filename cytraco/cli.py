"""CLI entry point for Cytraco application."""

import sys
from pathlib import Path

from cytraco import bootstrap, config, errors, ui


def app() -> None:
    """Run the main application.

    Bootstraps the application by ensuring configuration exists,
    prompting user for FTP if needed.
    """
    config_path = Path.home() / ".config" / "cytraco" / "config.toml"

    config_handler = config.TomlConfig()
    setup_ui = ui.setup.TerminalSetup()

    try:
        cfg = bootstrap.bootstrap_app(
            config_path,
            config_handler,
            setup_ui,
        )
        if cfg is None:
            print("\nSetup cancelled by user")
            sys.exit(0)

        print(f"\nConfiguration loaded. FTP: {cfg.ftp}W")
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
