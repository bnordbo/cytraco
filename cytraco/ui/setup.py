"""UI for initial setup and configuration. Alias: sup."""

from cytraco import bootstrap as bts
from cytraco import trainer as trn


class TerminalSetup:
    """Terminal-based setup UI using stdin/stdout."""

    @staticmethod
    def prompt_ftp() -> int | None:
        """Prompt user for FTP in watts, validating positive integer input.

        Returns:
            FTP value in watts (positive integer), or None if user exits.
        """
        print("\nFTP (Functional Threshold Power) not configured.")
        print("Please enter your FTP in watts (positive integer):")
        print('Type "(e)xit" to exit.')

        while True:
            try:
                value = input("> ").strip()
                if value.lower() == "e":
                    return None
                ftp_value = int(value)
                if ftp_value > 0:
                    return ftp_value
                print("FTP must be a positive number. Try again.")
            except ValueError:
                print("Invalid input. Please enter a positive integer.")
            except (KeyboardInterrupt, EOFError):
                return None

    @staticmethod
    def prompt_trainer_selection(
        trainers: list[trn.TrainerInfo],
    ) -> trn.TrainerInfo | None:
        """Prompt user to select from multiple trainers."""
        while True:
            print("\nMultiple trainers found:")
            for i, trainer in enumerate(trainers, 1):
                print(f"{i}. {trainer.name} at {trainer.address} ({trainer.rssi} dBm)")
            print(f"Enter number (1-{len(trainers)}), (r)etry, or (e)xit:")

            while True:
                try:
                    value = input("> ").strip().lower()
                    if value == "e":
                        return None
                    if value == "r":
                        break
                    try:
                        index = int(value) - 1
                        if 0 <= index < len(trainers):
                            return trainers[index]
                        print(f"Please enter a number between 1 and {len(trainers)}.")
                    except ValueError:
                        print("Invalid input. Please enter a number, (r)etry, or (e)xit.")
                except (KeyboardInterrupt, EOFError):
                    return None

    @staticmethod
    def prompt_single_trainer(trainer: trn.TrainerInfo) -> bts.UserChoice | None:
        """Prompt user to confirm single discovered trainer."""
        print(f"\nFound trainer: {trainer.name} at {trainer.address}")
        print("(c)ontinue, (r)etry, or (e)xit:")

        while True:
            try:
                value = input("> ").strip()
                choice = bts.UserChoice.from_input(value)
                if choice == bts.UserChoice.CONTINUE:
                    return choice
                if choice == bts.UserChoice.RETRY:
                    return choice
                if choice == bts.UserChoice.EXIT:
                    return None
                print("Invalid input. Please enter (c)ontinue, (r)etry, or (e)xit.")
            except (KeyboardInterrupt, EOFError):
                return None

    @staticmethod
    def prompt_no_trainers() -> bts.UserChoice | None:
        """Prompt user when no trainers found."""
        print("\nNo trainers found.")
        print("(r)etry or (e)xit:")

        while True:
            try:
                value = input("> ").strip()
                choice = bts.UserChoice.from_input(value)
                if choice == bts.UserChoice.RETRY:
                    return choice
                if choice == bts.UserChoice.EXIT:
                    return None
                print("Invalid input. Please enter (r)etry or (e)xit.")
            except (KeyboardInterrupt, EOFError):
                return None

    @staticmethod
    def prompt_connection_failed(address: str) -> bts.UserChoice | None:
        """Prompt user when configured trainer is unreachable."""
        print(f"\nCannot connect to trainer at {address}")
        print("(r)etry, (s)can, or (e)xit:")

        while True:
            try:
                value = input("> ").strip()
                choice = bts.UserChoice.from_input(value)
                if choice in (bts.UserChoice.RETRY, bts.UserChoice.SCAN):
                    return choice
                if choice == bts.UserChoice.EXIT:
                    return None
                print("Invalid input. Please enter (r)etry, (s)can, or (e)xit.")
            except (KeyboardInterrupt, EOFError):
                return None
