"""UI for initial setup and configuration. Alias: sup."""

from cytraco.trainer import TrainerInfo, TrainerResult, TrainerSelected, UserAction


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

    def prompt_reconnect(self, address: str) -> TrainerResult:
        """Ask user how to proceed when configured trainer is unreachable.

        Args:
            address: The BLE address of the unreachable trainer.

        Returns:
            User's choice: RETRY, SCAN, EXIT, or DEMO.
        """
        print(f"\nTrainer at {address} not found.")
        print("(r)etry, (s)can for new, (e)xit, or (c)ontinue in demo mode?")

        while True:
            try:
                value = input("> ").strip().lower()
                if value == "r":
                    return UserAction.RETRY
                if value == "s":
                    return UserAction.SCAN
                if value == "e":
                    return UserAction.EXIT
                if value == "c":
                    return UserAction.DEMO
                print("Invalid choice. Enter r, s, e, or c.")
            except (KeyboardInterrupt, EOFError):
                return UserAction.EXIT

    def prompt_trainer_selection(self, trainers: list[TrainerInfo]) -> TrainerResult:
        """Show discovered trainers and let user select one.

        Args:
            trainers: List of discovered trainers (may be empty).

        Returns:
            TrainerSelected with chosen trainer, or UserAction (RETRY, EXIT, DEMO).
        """
        if len(trainers) == 0:
            print("\nNo trainers found.")
            print("(r)etry, (e)xit, or (c)ontinue in demo mode?")
            return self._prompt_no_trainers()

        if len(trainers) == 1:
            trainer = trainers[0]
            print(f"\nFound {trainer.name} at {trainer.address}")
            print("(r)etry, (e)xit, or (c)ontinue?")
            return self._prompt_single_trainer(trainer)

        print("\nFound multiple trainers:")
        for i, trainer in enumerate(trainers, 1):
            print(f"  {i}. {trainer.name} at {trainer.address}")
        print(f"Enter 1-{len(trainers)} to select, (r)etry, or (e)xit.")
        return self._prompt_multiple_trainers(trainers)

    def _prompt_no_trainers(self) -> TrainerResult:
        while True:
            try:
                value = input("> ").strip().lower()
                if value == "r":
                    return UserAction.RETRY
                if value == "e":
                    return UserAction.EXIT
                if value == "c":
                    return UserAction.DEMO
                print("Invalid choice. Enter r, e, or c.")
            except (KeyboardInterrupt, EOFError):
                return UserAction.EXIT

    def _prompt_single_trainer(self, trainer: TrainerInfo) -> TrainerResult:
        while True:
            try:
                value = input("> ").strip().lower()
                if value == "r":
                    return UserAction.RETRY
                if value == "e":
                    return UserAction.EXIT
                if value == "c":
                    return TrainerSelected(trainer=trainer)
                print("Invalid choice. Enter r, e, or c.")
            except (KeyboardInterrupt, EOFError):
                return UserAction.EXIT

    def _prompt_multiple_trainers(self, trainers: list[TrainerInfo]) -> TrainerResult:
        while True:
            try:
                value = input("> ").strip().lower()
                if value == "r":
                    return UserAction.RETRY
                if value == "e":
                    return UserAction.EXIT
                try:
                    idx = int(value)
                    if 1 <= idx <= len(trainers):
                        return TrainerSelected(trainer=trainers[idx - 1])
                    print(f"Enter a number between 1 and {len(trainers)}.")
                except ValueError:
                    print(f"Invalid choice. Enter 1-{len(trainers)}, r, or e.")
            except (KeyboardInterrupt, EOFError):
                return UserAction.EXIT
