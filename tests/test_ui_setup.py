"""Tests for setup UI."""

import pytest

from cytraco.trainer import TrainerSelected, UserAction
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
    """TerminalSetup should return None when user types 'e'."""
    monkeypatch.setattr("builtins.input", lambda _: "e")

    setup = TerminalSetup()
    result = setup.prompt_ftp()

    assert result is None




def test_prompt_ftp_keyboard_interrupt(monkeypatch: pytest.MonkeyPatch) -> None:
    """TerminalSetup should return None on keyboard interrupt."""

    def raise_interrupt(_: str) -> str:
        raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", raise_interrupt)

    setup = TerminalSetup()
    result = setup.prompt_ftp()

    assert result is None


def test_prompt_ftp_eof_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """TerminalSetup should return None on EOF."""

    def raise_eof(_: str) -> str:
        raise EOFError

    monkeypatch.setattr("builtins.input", raise_eof)

    setup = TerminalSetup()
    result = setup.prompt_ftp()

    assert result is None


# prompt_reconnect tests


def test_prompt_reconnect_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    """prompt_reconnect returns RETRY when user types 'r'."""
    monkeypatch.setattr("builtins.input", lambda _: "r")
    setup = TerminalSetup()
    result = setup.prompt_reconnect(generate.mac_address())
    assert result == UserAction.RETRY


def test_prompt_reconnect_scan(monkeypatch: pytest.MonkeyPatch) -> None:
    """prompt_reconnect returns SCAN when user types 's'."""
    monkeypatch.setattr("builtins.input", lambda _: "s")
    setup = TerminalSetup()
    result = setup.prompt_reconnect(generate.mac_address())
    assert result == UserAction.SCAN


def test_prompt_reconnect_exit(monkeypatch: pytest.MonkeyPatch) -> None:
    """prompt_reconnect returns EXIT when user types 'e'."""
    monkeypatch.setattr("builtins.input", lambda _: "e")
    setup = TerminalSetup()
    result = setup.prompt_reconnect(generate.mac_address())
    assert result == UserAction.EXIT


def test_prompt_reconnect_demo(monkeypatch: pytest.MonkeyPatch) -> None:
    """prompt_reconnect returns DEMO when user types 'c'."""
    monkeypatch.setattr("builtins.input", lambda _: "c")
    setup = TerminalSetup()
    result = setup.prompt_reconnect(generate.mac_address())
    assert result == UserAction.DEMO


def test_prompt_reconnect_invalid_then_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    """prompt_reconnect rejects invalid input then accepts valid."""
    inputs = ["x", "r"]
    input_iter = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(input_iter))
    setup = TerminalSetup()
    result = setup.prompt_reconnect(generate.mac_address())
    assert result == UserAction.RETRY


def test_prompt_reconnect_keyboard_interrupt(monkeypatch: pytest.MonkeyPatch) -> None:
    """prompt_reconnect returns EXIT on keyboard interrupt."""

    def raise_interrupt(_: str) -> str:
        raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", raise_interrupt)
    setup = TerminalSetup()
    result = setup.prompt_reconnect(generate.mac_address())
    assert result == UserAction.EXIT


# prompt_trainer_selection tests


def test_prompt_trainer_selection_no_trainers_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    """prompt_trainer_selection returns RETRY when no trainers and user types 'r'."""
    monkeypatch.setattr("builtins.input", lambda _: "r")
    setup = TerminalSetup()
    result = setup.prompt_trainer_selection([])
    assert result == UserAction.RETRY


def test_prompt_trainer_selection_no_trainers_demo(monkeypatch: pytest.MonkeyPatch) -> None:
    """prompt_trainer_selection returns DEMO when no trainers and user types 'c'."""
    monkeypatch.setattr("builtins.input", lambda _: "c")
    setup = TerminalSetup()
    result = setup.prompt_trainer_selection([])
    assert result == UserAction.DEMO


def test_prompt_trainer_selection_single_continue(monkeypatch: pytest.MonkeyPatch) -> None:
    """prompt_trainer_selection returns TrainerSelected for single trainer."""
    trainer = generate.trainer_info()
    monkeypatch.setattr("builtins.input", lambda _: "c")
    setup = TerminalSetup()
    result = setup.prompt_trainer_selection([trainer])
    assert isinstance(result, TrainerSelected)
    assert result.trainer == trainer


def test_prompt_trainer_selection_single_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    """prompt_trainer_selection returns RETRY for single trainer when user retries."""
    trainer = generate.trainer_info()
    monkeypatch.setattr("builtins.input", lambda _: "r")
    setup = TerminalSetup()
    result = setup.prompt_trainer_selection([trainer])
    assert result == UserAction.RETRY


def test_prompt_trainer_selection_multiple_select_first(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """prompt_trainer_selection returns TrainerSelected for first trainer."""
    trainers = [generate.trainer_info() for _ in range(3)]
    monkeypatch.setattr("builtins.input", lambda _: "1")
    setup = TerminalSetup()
    result = setup.prompt_trainer_selection(trainers)
    assert isinstance(result, TrainerSelected)
    assert result.trainer == trainers[0]


def test_prompt_trainer_selection_multiple_select_last(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """prompt_trainer_selection returns TrainerSelected for last trainer."""
    trainers = [generate.trainer_info() for _ in range(3)]
    monkeypatch.setattr("builtins.input", lambda _: "3")
    setup = TerminalSetup()
    result = setup.prompt_trainer_selection(trainers)
    assert isinstance(result, TrainerSelected)
    assert result.trainer == trainers[2]


def test_prompt_trainer_selection_multiple_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    """prompt_trainer_selection returns RETRY for multiple trainers."""
    trainers = [generate.trainer_info() for _ in range(3)]
    monkeypatch.setattr("builtins.input", lambda _: "r")
    setup = TerminalSetup()
    result = setup.prompt_trainer_selection(trainers)
    assert result == UserAction.RETRY


def test_prompt_trainer_selection_multiple_invalid_then_valid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """prompt_trainer_selection rejects invalid selection then accepts valid."""
    trainers = [generate.trainer_info() for _ in range(3)]
    inputs = ["0", "4", "abc", "2"]
    input_iter = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(input_iter))
    setup = TerminalSetup()
    result = setup.prompt_trainer_selection(trainers)
    assert isinstance(result, TrainerSelected)
    assert result.trainer == trainers[1]
