"""Integration-style tests for cli_transform --file flag."""
import argparse
import json
import os
import tempfile
import pytest
from envsnap.cli_transform import cmd_transform
from envsnap.export import to_json
from envsnap.snapshot import capture


def _ns(**kw):
    defaults = dict(operation="upper", file=None, keys=None, summary=False)
    defaults.update(kw)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def snap_file(tmp_path):
    snap = {"label": "test", "env": {"greeting": "hello", "name": "world"}}
    data = to_json(snap)
    p = tmp_path / "snap.json"
    p.write_text(data)
    return str(p)


def test_cmd_transform_reads_file(snap_file, capsys):
    cmd_transform(_ns(operation="upper", file=snap_file))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["greeting"] == "HELLO"
    assert data["name"] == "WORLD"


def test_cmd_transform_file_with_keys(snap_file, capsys):
    cmd_transform(_ns(operation="upper", file=snap_file, keys=["greeting"]))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["greeting"] == "HELLO"
    assert data["name"] == "world"


def test_cmd_transform_file_summary(snap_file, capsys):
    cmd_transform(_ns(operation="strip", file=snap_file, summary=True))
    out = capsys.readouterr().out
    assert "Applied" in out
