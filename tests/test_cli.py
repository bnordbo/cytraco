"""Tests for CLI argument parsing."""

import pytest

from cytraco.cli import CliArgs, parse_args


def test_parse_args_no_flags() -> None:
    """parse_args should default demo to False."""
    args = parse_args([])
    assert isinstance(args, CliArgs)
    assert args.demo is False


def test_parse_args_demo_flag() -> None:
    """parse_args should parse --demo flag."""
    args = parse_args(["--demo"])
    assert isinstance(args, CliArgs)
    assert args.demo is True


def test_parse_args_help_flag() -> None:
    """parse_args should handle --help flag."""
    with pytest.raises(SystemExit) as exc_info:
        parse_args(["--help"])
    assert exc_info.value.code == 0
