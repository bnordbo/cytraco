"""UI for initial setup and configuration. Alias: sup."""

from cytraco import trainer as trn


class TerminalSetup:
    """Terminal-based setup UI using stdin/stdout."""

    def prompt_ftp(self) -> int | None:
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
                    return await self.prompt_trainer_selection(trainers)
                try:
                    index = int(value) - 1
                    if 0 <= index < len(trainers):
                        return trainers[index]
                    print(f"Please enter a number between 1 and {len(trainers)}.")
                except ValueError:
                    print("Invalid input. Please enter a number, (r)etry, or (e)xit.")
            except (KeyboardInterrupt, EOFError):
                return None

    async def prompt_single_trainer(self, trainer: trn.TrainerInfo) -> bool | None:
        """Prompt user to confirm single discovered trainer.

        Args:
            trainer: The single discovered trainer.

        Returns:
            True to continue, False to retry scan, None to exit.
        """
        print(f"\nFound trainer: {trainer.name} at {trainer.address}")
        print("(c)ontinue, (r)etry, or (e)xit:")

        while True:
            try:
                value = input("> ").strip().lower()
                if value == "c":
                    return True
                if value == "r":
                    return False
                if value == "e":
                    return None
                print("Invalid input. Please enter (c)ontinue, (r)etry, or (e)xit.")
            except (KeyboardInterrupt, EOFError):
                return None

    async def prompt_no_trainers(self) -> bool | None:
        """Prompt user when no trainers found.

        Returns:
            True to retry scan, None to exit.
        """
        print("\nNo trainers found.")
        print("(r)etry or (e)xit:")

        while True:
            try:
                value = input("> ").strip().lower()
                if value == "r":
                    return True
                if value == "e":
                    return None
                print("Invalid input. Please enter (r)etry or (e)xit.")
            except (KeyboardInterrupt, EOFError):
                return None

    async def prompt_connection_failed(self, address: str) -> str | None:
        """Prompt user when configured trainer is unreachable.

        Args:
            address: Device address of configured but unreachable trainer.

        Returns:
            'retry' to retry connection, 'scan' to scan for trainers, None to exit.
        """
        print(f"\nCannot connect to trainer at {address}")
        print("(r)etry, (s)can, or (e)xit:")

        while True:
            try:
                value = input("> ").strip().lower()
                if value == "r":
                    return "retry"
                if value == "s":
                    return "scan"
                if value == "e":
                    return None
                print("Invalid input. Please enter (r)etry, (s)can, or (e)xit.")
            except (KeyboardInterrupt, EOFError):
                return None
