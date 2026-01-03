"""UI for initial setup and configuration."""

from cytraco import errors


class TerminalSetup:
    """Terminal-based setup UI using stdin/stdout."""

    def prompt_ftp(self) -> int:
        """Prompt user for FTP in watts, validating positive integer input.

        Returns:
            FTP value in watts (positive integer).

        Raises:
            ConfigError: If user exits via "(e)exit", "e", or Ctrl-C.
        """
        print("\nFTP (Functional Threshold Power) not configured.")
        print("Please enter your FTP in watts (positive integer):")
        print('Type "(e)xit" to exit.')

        while True:
            try:
                value = input("> ").strip()

                if value.lower() == "e":
                    raise errors.ConfigError("Setup cancelled by user")

                ftp_value = int(value)

                if ftp_value > 0:
                    return ftp_value

                print("FTP must be a positive number. Try again.")

            except ValueError:
                print("Invalid input. Please enter a positive integer.")
            except (KeyboardInterrupt, EOFError) as e:
                raise errors.ConfigError("Setup cancelled by user") from e
