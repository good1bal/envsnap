"""Tests for envsnap.cli_transform."""
import argparse
import json
import pytest
from unittest.mock import patch, MagicMock
from envsnap.cli_transform import cmd_transform, build_parser


def _ns(**kw):
    defaults = dict(operation="upper", file=None, keys=None, summary=False)
    defaults.update(kw)
    return argparse.Namespace(**defaults)


_FAKE_SNAP = {"env": {"foo": "hello", "bar": "world"}}


def test_cmd_transform_upper(capsys):
    with patch("envsnap.cli_transform.capture", return_value=_FAKE_SNAP):
        cmd_transform(_ns(operation="upper"))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["foo"] == "HELLO"
    assert data["bar"] == "WORLD"


def test_cmd_transform_lower(capsys):
    snap = {"env": {"A": "ABC"}}
    with patch("envsnap.cli_transform.capture", return_value=snap):
        cmd_transform(_ns(operation="lower"))
    out = capsys.readouterr().out
    assert json.loads(out)["A"] == "abc"


def test_cmd_transform_strip(capsys):
    snap = {"env": {"K": "  val  "}}
    with patch("envsnap.cli_transform.capture", return_value=snap):
        cmd_transform(_ns(operation="strip"))
    out = capsys.readouterr().out
    assert json.loads(out)["K"] == "val"


def test_cmd_transform_selected_keys(capsys):
    with patch("envsnap.cli_transform.capture", return_value=_FAKE_SNAP):
        cmd_transform(_ns(operation="upper", keys=["foo"]))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["foo"] == "HELLO"
    assert data["bar"] == "world"


def test_cmd_transform_summary(capsys):
    with patch("envsnap.cli_transform.capture", return_value=_FAKE_SNAP):
        cmd_transform(_ns(operation="upper", summary=True))
    out = capsys.readouterr().out
    assert "Applied" in out


def test_cmd_transform_unknown_operation():
    with patch("envsnap.cli_transform.capture", return_value=_FAKE_SNAP):
        with pytest.raises(SystemExit):
            cmd_transform(_ns(operation="reverse"))


def test_build_parser_returns_parser():
    p = build_parser()
    assert isinstance(p, argparse.ArgumentParser)
