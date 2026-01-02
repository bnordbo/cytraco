"""Tests for exception hierarchy."""

import pytest

from cytraco.errors import AppRunnerError, CytracoError, PowerMeterError


def test_cytraco_error_is_exception() -> None:
    """CytracoError should inherit from Exception."""
    assert issubclass(CytracoError, Exception)
    error = CytracoError("test message")
    assert str(error) == "test message"


def test_power_meter_error_hierarchy() -> None:
    """PowerMeterError should inherit from CytracoError."""
    assert issubclass(PowerMeterError, CytracoError)
    assert issubclass(PowerMeterError, Exception)


def test_app_runner_error_hierarchy() -> None:
    """AppRunnerError should inherit from CytracoError."""
    assert issubclass(AppRunnerError, CytracoError)
    assert issubclass(AppRunnerError, Exception)


def test_catch_all_cytraco_errors() -> None:
    """All Cytraco exceptions should be catchable with CytracoError."""
    with pytest.raises(CytracoError):
        raise PowerMeterError("test")

    with pytest.raises(CytracoError):
        raise AppRunnerError("test")


def test_exception_wrapping() -> None:
    """Exceptions should support wrapping with __cause__."""
    original = ValueError("original error")

    with pytest.raises(PowerMeterError) as exc_info:
        raise PowerMeterError("wrapped error") from original

    assert str(exc_info.value) == "wrapped error"
    assert exc_info.value.__cause__ is original
    assert isinstance(exc_info.value.__cause__, ValueError)
