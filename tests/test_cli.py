"""Bare `wingfoot` greets with the full help instead of an argparse error."""
import urllib.error

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


def test_sign_reports_connection_error_cleanly(monkeypatch, capsys):
    """`wingfoot sign <unreachable>` should print a clean error and exit 1,
    not surface a urllib traceback to the user."""
    def boom(*args, **kwargs):
        raise urllib.error.URLError("Connection refused")

    monkeypatch.setattr("wingfoot.cli._http.request", boom)
    rc = main(["sign", "http://127.0.0.1:1/"])
    assert rc == 1
    err = capsys.readouterr().err
    assert "Could not reach http://127.0.0.1:1/" in err
    assert "Connection refused" in err


def test_sign_print_only_needs_no_network(monkeypatch):
    """--print-only must never touch the network."""
    def boom(*args, **kwargs):
        raise AssertionError("network should not be used with --print-only")

    monkeypatch.setattr("wingfoot.cli._http.request", boom)
    assert main(["sign", "https://example.com/", "--print-only"]) == 0


# --- init must not destroy an existing key ----------------------------------

def test_init_refuses_to_overwrite_an_existing_identity(monkeypatch, capsys):
    """Re-running `init` reads as harmless but replaces the private key, changing the
    keyid and invalidating any verifier registration made against the old one."""
    saved = []
    monkeypatch.setattr("wingfoot.cli.identity_exists", lambda *a, **k: True)
    monkeypatch.setattr("wingfoot.cli.save_identity", lambda *a, **k: saved.append(a))

    rc = main(["init", "--agent", "https://bot.example"])

    assert rc == 2
    assert saved == [], "init wrote over an existing identity"
    err = capsys.readouterr().err
    assert "already exists" in err
    assert "wingfoot identity" in err, "should point at the non-destructive alternative"


def test_init_force_replaces_the_identity(monkeypatch):
    saved = []
    monkeypatch.setattr("wingfoot.cli.identity_exists", lambda *a, **k: True)
    monkeypatch.setattr("wingfoot.cli.save_identity",
                        lambda ident, *a, **k: saved.append(ident) or "/tmp/home")

    assert main(["init", "--agent", "https://bot.example", "--force"]) == 0
    assert len(saved) == 1


# --- identity updates keep the key ------------------------------------------

def test_identity_update_keeps_the_same_key(monkeypatch, capsys):
    from wingfoot.keys import ephemeral_identity

    identity = ephemeral_identity(agent_url="https://old.example")
    original_key = identity.private_key
    original_keyid = identity.keyid
    saved = []
    monkeypatch.setattr("wingfoot.cli.load_identity", lambda *a, **k: identity)
    monkeypatch.setattr("wingfoot.cli.save_identity",
                        lambda ident, *a, **k: saved.append(ident) or "/tmp/home")

    rc = main(["identity", "--agent", "https://new.example",
               "--user-agent", "MyBot/1.0 (+https://new.example)"])

    assert rc == 0
    assert saved[0].private_key is original_key
    assert saved[0].keyid == original_keyid
    assert saved[0].agent_url == "https://new.example"
    assert saved[0].user_agent == "MyBot/1.0 (+https://new.example)"
    assert "register" in capsys.readouterr().out, "should prompt to re-register after a change"
