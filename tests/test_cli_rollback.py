"""Tests for envsnap.cli_rollback."""
from __future__ import annotations

import json
import argparse
import pytest

from envsnap.cli_rollback import cmd_rollback, build_parser
from envsnap.export import to_json


def _snap(label: str, env: dict) -> dict:
    return {"label": label, "env": env, "meta": {}}


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {
        "current": None,
        "target": None,
        "keys": None,
        "output": None,
        "json": False,
        "summary": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def snap_files(tmp_path):
    current = _snap("new", {"A": "2", "B": "keep", "EXTRA": "x"})
    target = _snap("old", {"A": "1", "B": "keep"})
    cur_path = tmp_path / "current.json"
    tgt_path = tmp_path / "target.json"
    cur_path.write_text(to_json(current))
    tgt_path.write_text(to_json(target))
    return str(cur_path), str(tgt_path)


def test_cmd_rollback_prints_changes(snap_files, capsys):
    cur, tgt = snap_files
    ns = _ns(current=cur, target=tgt)
    cmd_rollback(ns)
    out = capsys.readouterr().out
    assert "A" in out or "EXTRA" in out


def test_cmd_rollback_json_output(snap_files, capsys):
    cur, tgt = snap_files
    ns = _ns(current=cur, target=tgt, json=True)
    cmd_rollback(ns)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "reverted" in data
    assert data["reverted"]["A"] == "1"


def test_cmd_rollback_summary_flag(snap_files, capsys):
    cur, tgt = snap_files
    ns = _ns(current=cur, target=tgt, summary=True)
    cmd_rollback(ns)
    out = capsys.readouterr().out
    assert "Rollback summary" in out


def test_cmd_rollback_output_writes_file(snap_files, tmp_path):
    cur, tgt = snap_files
    out_path = str(tmp_path / "reverted.json")
    ns = _ns(current=cur, target=tgt, output=out_path)
    cmd_rollback(ns)
    data = json.loads(open(out_path).read())
    assert data["env"]["A"] == "1"
    assert "EXTRA" not in data["env"]


def test_cmd_rollback_missing_file_exits(tmp_path):
    ns = _ns(current="no_such.json", target="also_missing.json")
    with pytest.raises(SystemExit) as exc_info:
        cmd_rollback(ns)
    assert exc_info.value.code == 1


def test_build_parser_returns_parser():
    p = build_parser()
    assert p is not None
    ns = p.parse_args(["a.json", "b.json", "--summary"])
    assert ns.summary is True
