"""Tests for envsnap.cli_lint."""
import argparse
import pytest
from unittest.mock import patch, MagicMock
from envsnap.cli_lint import cmd_lint, build_parser


def _ns(**kwargs):
    defaults = {
        "file": None,
        "allow_lowercase": False,
        "max_value_length": None,
        "forbidden": None,
        "json": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _clean_snap():
    return {"label": "test", "env": {"APP_ENV": "production"}}


def _dirty_snap():
    return {"label": "test", "env": {"bad_key": "value"}}


def test_cmd_lint_clean_exits_zero(capsys):
    with patch("envsnap.cli_lint.capture", return_value=_clean_snap()):
        cmd_lint(_ns())
    out = capsys.readouterr().out
    assert "no issues" in out


def test_cmd_lint_dirty_exits_one():
    with patch("envsnap.cli_lint.capture", return_value=_dirty_snap()):
        with pytest.raises(SystemExit) as exc:
            cmd_lint(_ns())
    assert exc.value.code == 1


def test_cmd_lint_from_file(tmp_path, capsys):
    from envsnap.snapshot import save
    snap_file = tmp_path / "snap.json"
    save(_clean_snap(), str(snap_file))
    cmd_lint(_ns(file=str(snap_file)))
    out = capsys.readouterr().out
    assert "no issues" in out


def test_cmd_lint_json_output(capsys):
    import json
    with patch("envsnap.cli_lint.capture", return_value=_dirty_snap()):
        with pytest.raises(SystemExit):
            cmd_lint(_ns(json=True))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert isinstance(data, list)
    assert data[0]["key"] == "bad_key"


def test_cmd_lint_forbidden_pattern_error():
    snap = {"label": "t", "env": {"SECRET": "password123"}}
    with patch("envsnap.cli_lint.capture", return_value=snap):
        with pytest.raises(SystemExit) as exc:
            cmd_lint(_ns(forbidden=["password"]))
    assert exc.value.code == 1


def test_build_parser_returns_parser():
    p = build_parser()
    assert isinstance(p, argparse.ArgumentParser)


def test_build_parser_defaults():
    p = build_parser()
    args = p.parse_args([])
    assert args.allow_lowercase is False
    assert args.max_value_length is None
    assert args.forbidden is None
