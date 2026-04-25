"""Tests for envsnap.cli_required."""
import argparse
import json
import pytest

from envsnap.cli_required import cmd_check, build_parser
from envsnap.export import to_json
from envsnap.snapshot import capture


def _snap(**kwargs):
    return {"label": "test", "captured_at": "2024-01-01T00:00:00", **kwargs}


def _ns(**kwargs):
    defaults = dict(
        keys=[],
        file=None,
        defaults=None,
        apply_defaults=False,
        json=False,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_check_all_present_exits_zero(tmp_path, capsys):
    snap = _snap(FOO="1", BAR="2")
    f = tmp_path / "snap.json"
    f.write_text(to_json(snap))
    ns = _ns(keys=["FOO", "BAR"], file=str(f))
    cmd_check(ns)  # should not raise
    out = capsys.readouterr().out
    assert "Present" in out


def test_cmd_check_missing_key_exits_one(tmp_path):
    snap = _snap(FOO="1")
    f = tmp_path / "snap.json"
    f.write_text(to_json(snap))
    ns = _ns(keys=["FOO", "MISSING"], file=str(f))
    with pytest.raises(SystemExit) as exc:
        cmd_check(ns)
    assert exc.value.code == 1


def test_cmd_check_json_output(tmp_path, capsys):
    snap = _snap(FOO="1")
    f = tmp_path / "snap.json"
    f.write_text(to_json(snap))
    ns = _ns(keys=["FOO"], file=str(f), json=True)
    cmd_check(ns)
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["satisfied"] is True
    assert "FOO" in payload["present"]


def test_cmd_check_apply_defaults_satisfies_missing(tmp_path, capsys):
    snap = _snap(FOO="1")
    f = tmp_path / "snap.json"
    f.write_text(to_json(snap))
    ns = _ns(
        keys=["FOO", "BAR"],
        file=str(f),
        defaults=["BAR=fallback"],
        apply_defaults=True,
        json=True,
    )
    cmd_check(ns)  # should not raise SystemExit
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["satisfied"] is True
    assert payload["defaults_applied"] == {"BAR": "fallback"}


def test_cmd_check_invalid_default_format_exits_two(tmp_path):
    snap = _snap(FOO="1")
    f = tmp_path / "snap.json"
    f.write_text(to_json(snap))
    ns = _ns(keys=["FOO"], file=str(f), defaults=["BADFORMAT"])
    with pytest.raises(SystemExit) as exc:
        cmd_check(ns)
    assert exc.value.code == 2


def test_build_parser_returns_parser():
    parser = build_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_build_parser_parses_keys():
    parser = build_parser()
    args = parser.parse_args(["FOO", "BAR"])
    assert args.keys == ["FOO", "BAR"]
    assert args.apply_defaults is False
    assert args.json is False
