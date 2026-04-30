"""Tests for envsnap.cli_protect."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envsnap.cli_protect import cmd_check, cmd_list, cmd_protect, cmd_unprotect
from envsnap.env_protect import save_protected
from envsnap.export import to_json


def _snap(**kwargs):
    return {"APP": "demo", "DB_PASS": "secret", **kwargs}


def _ns(**kwargs):
    import argparse
    defaults = dict(store=None, json=False, file=None, keys=[])
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _write_snap(path: Path, env: dict) -> Path:
    snap_file = path / "snap.json"
    snap_file.write_text(to_json({"env": env, "label": "test", "captured_at": "now", "checksum": "x"}))
    return snap_file


# ---------------------------------------------------------------------------
# cmd_protect
# ---------------------------------------------------------------------------

def test_cmd_protect_prints_summary(tmp_path, capsys):
    snap_file = _write_snap(tmp_path, _snap())
    ns = _ns(store=str(tmp_path), keys=["APP"], file=str(snap_file))
    cmd_protect(ns)
    out = capsys.readouterr().out
    assert "Protected keys" in out


def test_cmd_protect_json_output(tmp_path, capsys):
    snap_file = _write_snap(tmp_path, _snap())
    ns = _ns(store=str(tmp_path), keys=["APP"], file=str(snap_file), json=True)
    cmd_protect(ns)
    data = json.loads(capsys.readouterr().out)
    assert "protected" in data


# ---------------------------------------------------------------------------
# cmd_unprotect
# ---------------------------------------------------------------------------

def test_cmd_unprotect_removes_key(tmp_path, capsys):
    save_protected(["APP", "DB_PASS"], tmp_path)
    ns = _ns(store=str(tmp_path), keys=["APP"])
    cmd_unprotect(ns)
    from envsnap.env_protect import load_protected
    remaining = load_protected(tmp_path)
    assert "APP" not in remaining
    assert "DB_PASS" in remaining


def test_cmd_unprotect_prints_count(tmp_path, capsys):
    save_protected(["APP"], tmp_path)
    ns = _ns(store=str(tmp_path), keys=["APP"])
    cmd_unprotect(ns)
    out = capsys.readouterr().out
    assert "1" in out


# ---------------------------------------------------------------------------
# cmd_list
# ---------------------------------------------------------------------------

def test_cmd_list_empty(tmp_path, capsys):
    ns = _ns(store=str(tmp_path))
    cmd_list(ns)
    assert "no protected keys" in capsys.readouterr().out


def test_cmd_list_shows_keys(tmp_path, capsys):
    save_protected(["APP", "DB_PASS"], tmp_path)
    ns = _ns(store=str(tmp_path))
    cmd_list(ns)
    out = capsys.readouterr().out
    assert "APP" in out


def test_cmd_list_json(tmp_path, capsys):
    save_protected(["APP"], tmp_path)
    ns = _ns(store=str(tmp_path), json=True)
    cmd_list(ns)
    data = json.loads(capsys.readouterr().out)
    assert "APP" in data


# ---------------------------------------------------------------------------
# cmd_check
# ---------------------------------------------------------------------------

def test_cmd_check_no_violations_exits_zero(tmp_path):
    env = _snap()
    orig = _write_snap(tmp_path, env)
    upd_path = tmp_path / "updated.json"
    upd_path.write_text(to_json({"env": env, "label": "t", "captured_at": "n", "checksum": "x"}))
    save_protected(["APP"], tmp_path)
    ns = _ns(store=str(tmp_path), original=str(orig), updated=str(upd_path))
    cmd_check(ns)  # should not raise


def test_cmd_check_violation_exits_one(tmp_path):
    orig_env = _snap()
    upd_env = _snap(APP="changed")
    orig = _write_snap(tmp_path, orig_env)
    upd_path = tmp_path / "updated.json"
    upd_path.write_text(to_json({"env": upd_env, "label": "t", "captured_at": "n", "checksum": "x"}))
    save_protected(["APP"], tmp_path)
    ns = _ns(store=str(tmp_path), original=str(orig), updated=str(upd_path))
    with pytest.raises(SystemExit) as exc:
        cmd_check(ns)
    assert exc.value.code == 1
