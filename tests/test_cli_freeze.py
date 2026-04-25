"""Tests for envsnap.cli_freeze."""
import json
import pytest

from envsnap.cli_freeze import cmd_freeze, cmd_unfreeze, cmd_check, cmd_list
from envsnap.env_freeze import save_frozen


def _ns(**kwargs):
    import argparse
    defaults = {"store": None, "summary": False, "keys": [], "show_values": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def snap_file(tmp_path):
    data = {"label": "test", "env": {"API_KEY": "abc", "DB_HOST": "localhost"}}
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data))
    return str(p)


@pytest.fixture()
def store(tmp_path):
    return str(tmp_path / "store")


def test_cmd_freeze_all_keys(snap_file, store, capsys):
    args = _ns(file=snap_file, store=store, keys=[])
    cmd_freeze(args)
    out = capsys.readouterr().out
    assert "API_KEY" in out
    assert "DB_HOST" in out


def test_cmd_freeze_selected_key(snap_file, store, capsys):
    args = _ns(file=snap_file, store=store, keys=["API_KEY"])
    cmd_freeze(args)
    out = capsys.readouterr().out
    assert "API_KEY" in out
    assert "DB_HOST" not in out


def test_cmd_freeze_summary_flag(snap_file, store, capsys):
    args = _ns(file=snap_file, store=store, keys=[], summary=True)
    cmd_freeze(args)
    out = capsys.readouterr().out
    assert "Frozen" in out


def test_cmd_freeze_missing_key_shows_skipped(snap_file, store, capsys):
    args = _ns(file=snap_file, store=store, keys=["NOPE"])
    cmd_freeze(args)
    out = capsys.readouterr().out
    assert "skipped" in out


def test_cmd_unfreeze_removes_key(store, capsys):
    save_frozen({"API_KEY": "abc"}, store)
    args = _ns(store=store, keys=["API_KEY"])
    cmd_unfreeze(args)
    out = capsys.readouterr().out
    assert "unfrozen" in out


def test_cmd_unfreeze_no_match(store, capsys):
    save_frozen({}, store)
    args = _ns(store=store, keys=["NOPE"])
    cmd_unfreeze(args)
    out = capsys.readouterr().out
    assert "No matching" in out


def test_cmd_check_no_violations(snap_file, store, capsys):
    save_frozen({"API_KEY": "abc", "DB_HOST": "localhost"}, store)
    args = _ns(file=snap_file, store=store)
    cmd_check(args)  # should not raise SystemExit
    out = capsys.readouterr().out
    assert "OK" in out


def test_cmd_check_violation_exits_one(snap_file, store):
    save_frozen({"API_KEY": "different_value"}, store)
    args = _ns(file=snap_file, store=store)
    with pytest.raises(SystemExit) as exc:
        cmd_check(args)
    assert exc.value.code == 1


def test_cmd_list_no_frozen(store, capsys):
    args = _ns(store=store)
    cmd_list(args)
    out = capsys.readouterr().out
    assert "No keys" in out


def test_cmd_list_masks_values_by_default(store, capsys):
    save_frozen({"SECRET": "topsecret"}, store)
    args = _ns(store=store, show_values=False)
    cmd_list(args)
    out = capsys.readouterr().out
    assert "SECRET" in out
    assert "***" in out
    assert "topsecret" not in out
