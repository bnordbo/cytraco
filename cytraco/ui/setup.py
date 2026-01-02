"""UI for initial setup and configuration."""

from cytraco import errors


class TerminalSetup:
    """Terminal-based setup UI using stdin/stdout."""

    def prompt_ftp(self) -> int:
        """Prompt user for FTP in watts.

        Validates that input is:
        - A valid integer
        - Positive (> 0)
        - Allows "(e)exit" or "e" to exit

        Returns:
            FTP value in watts (positive integer).

        Raises:
            ConfigError: If user exits via "(e)exit", "e", or Ctrl-C.
        """
        print("\nFTP (Functional Threshold Power) not configured.")
        print("Please enter your FTP in watts (positive integer):")
        print('Type "(e)exit" or "e" to exit.')

        while True:
            try:
                value = input("> ").strip()

                # Check for exit commands
                if value.lower() in ("e", "exit", "(e)exit"):
                    raise errors.ConfigError("Setup cancelled by user")

                # Try to parse as integer
                ftp_value = int(value)

                # Validate positive
                if ftp_value > 0:
                    return ftp_value

                print("FTP must be a positive number. Try again.")

            except ValueError:
                print("Invalid input. Please enter a positive integer.")
            except (KeyboardInterrupt, EOFError) as e:
                raise errors.ConfigError("Setup cancelled by user") from e
