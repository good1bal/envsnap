"""Tests for envsnap.cli_pin module."""
import argparse
import os

import pytest

from envsnap.cli_pin import cmd_check, cmd_list, cmd_pin, cmd_unpin
from envsnap.pin import load_pins, pin_key


def _ns(**kwargs):
    defaults = {"dir": ".", "key": None, "value": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_pin_explicit_value(tmp_path, capsys):
    args = _ns(dir=str(tmp_path), key="FOO", value="bar")
    cmd_pin(args)
    assert load_pins(str(tmp_path))["FOO"] == "bar"
    out = capsys.readouterr().out
    assert "FOO" in out


def test_cmd_pin_from_env(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("MY_VAR", "from_env")
    args = _ns(dir=str(tmp_path), key="MY_VAR", value=None)
    cmd_pin(args)
    assert load_pins(str(tmp_path))["MY_VAR"] == "from_env"


def test_cmd_pin_missing_key_and_env(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("GHOST_KEY", raising=False)
    args = _ns(dir=str(tmp_path), key="GHOST_KEY", value=None)
    cmd_pin(args)
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_unpin(tmp_path, capsys):
    pin_key("DEL_ME", "val", str(tmp_path))
    args = _ns(dir=str(tmp_path), key="DEL_ME")
    cmd_unpin(args)
    assert "DEL_ME" not in load_pins(str(tmp_path))


def test_cmd_list_empty(tmp_path, capsys):
    cmd_list(_ns(dir=str(tmp_path)))
    assert "No pins" in capsys.readouterr().out


def test_cmd_list_shows_pins(tmp_path, capsys):
    pin_key("K", "v", str(tmp_path))
    cmd_list(_ns(dir=str(tmp_path)))
    assert "K" in capsys.readouterr().out


def test_cmd_check_pass(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("STABLE", "yes")
    pin_key("STABLE", "yes", str(tmp_path))
    cmd_check(_ns(dir=str(tmp_path)))
    assert "match" in capsys.readouterr().out


def test_cmd_check_fail(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("STABLE", "no")
    pin_key("STABLE", "yes", str(tmp_path))
    cmd_check(_ns(dir=str(tmp_path)))
    assert "FAIL" in capsys.readouterr().out
