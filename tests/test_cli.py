"""Bare `wingfoot` greets with the full help instead of an argparse error."""
import pytest

from wingfoot.cli import main


def test_no_args_prints_full_help_and_exits_zero(capsys):
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "usage: wingfoot" in out
    for command in ("demo", "init", "doctor", "register"):
        assert command in out


def test_unknown_command_still_errors():
    with pytest.raises(SystemExit) as exc:
        main(["not-a-command"])
    assert exc.value.code == 2
