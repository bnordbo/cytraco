"""Tests for setup UI."""

import pytest

from cytraco import errors
from cytraco.ui.setup import TerminalSetup
from tests import generators as generate


def test_prompt_ftp_valid_input(monkeypatch: pytest.MonkeyPatch) -> None:
    """TerminalSetup should return FTP when valid input provided."""
    test_ftp = generate.ftp()
    monkeypatch.setattr("builtins.input", lambda _: str(test_ftp))

    setup = TerminalSetup()
    result = setup.prompt_ftp()

    assert result == test_ftp


def test_prompt_ftp_zero_then_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    """TerminalSetup should reject zero and accept valid input."""
    test_ftp = generate.ftp()
    inputs = ["0", str(test_ftp)]
    input_iter = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

    setup = TerminalSetup()
    result = setup.prompt_ftp()

    assert result == test_ftp


def test_prompt_ftp_negative_then_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    """TerminalSetup should reject negative and accept valid input."""
    test_ftp = generate.ftp()
    inputs = ["-100", str(test_ftp)]
    input_iter = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

    setup = TerminalSetup()
    result = setup.prompt_ftp()

    assert result == test_ftp


def test_prompt_ftp_non_numeric_then_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    """TerminalSetup should reject non-numeric and accept valid input."""
    test_ftp = generate.ftp()
    inputs = ["abc", "12.5", str(test_ftp)]
    input_iter = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

    setup = TerminalSetup()
    result = setup.prompt_ftp()

    assert result == test_ftp


def test_prompt_ftp_exit_with_e(monkeypatch: pytest.MonkeyPatch) -> None:
    """TerminalSetup should raise ConfigError when user types 'e'."""
    monkeypatch.setattr("builtins.input", lambda _: "e")

    setup = TerminalSetup()

    with pytest.raises(errors.ConfigError, match="cancelled by user"):
        setup.prompt_ftp()


def test_prompt_ftp_exit_with_exit(monkeypatch: pytest.MonkeyPatch) -> None:
    """TerminalSetup should raise ConfigError when user types 'exit'."""
    monkeypatch.setattr("builtins.input", lambda _: "exit")

    setup = TerminalSetup()

    with pytest.raises(errors.ConfigError, match="cancelled by user"):
        setup.prompt_ftp()


def test_prompt_ftp_exit_with_parentheses(monkeypatch: pytest.MonkeyPatch) -> None:
    """TerminalSetup should raise ConfigError when user types '(e)exit'."""
    monkeypatch.setattr("builtins.input", lambda _: "(e)exit")

    setup = TerminalSetup()

    with pytest.raises(errors.ConfigError, match="cancelled by user"):
        setup.prompt_ftp()


def test_prompt_ftp_keyboard_interrupt(monkeypatch: pytest.MonkeyPatch) -> None:
    """TerminalSetup should raise ConfigError on keyboard interrupt."""

    def raise_interrupt(_: str) -> str:
        raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", raise_interrupt)

    setup = TerminalSetup()

    with pytest.raises(errors.ConfigError, match="cancelled by user"):
        setup.prompt_ftp()


def test_prompt_ftp_eof_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """TerminalSetup should raise ConfigError on EOF."""

    def raise_eof(_: str) -> str:
        raise EOFError

    monkeypatch.setattr("builtins.input", raise_eof)

    setup = TerminalSetup()

    with pytest.raises(errors.ConfigError, match="cancelled by user"):
        setup.prompt_ftp()
