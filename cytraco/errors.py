"""Exception hierarchy for Cytraco. Alias: err"""


class CytracoError(Exception):
    """Base exception for all Cytraco errors.

    All custom exceptions in Cytraco inherit from this base class,
    allowing clients to catch all Cytraco-specific errors with a single
    except clause.
    """



class PowerMeterError(CytracoError):
    """Exception raised by PowerMeter protocol implementations.

    Raised when power meter operations fail, such as connection errors,
    device unavailability, or monitoring failures.
    """



class AppRunnerError(CytracoError):
    """Exception raised by AppRunner protocol implementations.

    Raised when the application runner cannot start or encounters
    a fatal error during execution.
    """



class DeviceError(CytracoError):
    """Exception raised during device connection or usage.

    Raised when a BLE operation on a device fails..
    """



class ConfigError(CytracoError):
    """Exception raised during configuration operations.

    Raised when configuration file operations fail (read, write, parse).
    """

