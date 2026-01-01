"""Exception hierarchy for Cytraco."""


class CytracoError(Exception):
    """Base exception for all Cytraco errors.

    All custom exceptions in Cytraco inherit from this base class,
    allowing clients to catch all Cytraco-specific errors with a single
    except clause.
    """

    pass


class PowerMeterError(CytracoError):
    """Exception raised by PowerMeter protocol implementations.

    Raised when power meter operations fail, such as connection errors,
    device unavailability, or monitoring failures.
    """

    pass


class AppRunnerError(CytracoError):
    """Exception raised by AppRunner protocol implementations.

    Raised when the application runner cannot start or encounters
    a fatal error during execution.
    """

    pass
