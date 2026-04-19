"""Tests for envsnap.cli_mask."""
import argparse
import json
import pytest
from unittest.mock import patch, MagicMock
from envsnap.cli_mask import cmd_mask, build_parser


def _ns(**kwargs):
    defaults = {
        "file": "snap.json",
        "keys": None,
        "placeholder": "***",
        "no_auto": False,
        "summary": False,
        "format": "json",
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _fake_snap(extra=None):
    env = {"APP_HOST": "localhost", "APP_SECRET": "abc"}
    if extra:
        env.update(extra)
    return {"label": "test", "env": env, "checksum": "x"}


def test_cmd_mask_auto_masks_secret(capsys):
    with patch("envsnap.cli_mask.load", return_value=_fake_snap()):
        cmd_mask(_ns())
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["env"]["APP_SECRET"] == "***"
    assert data["env"]["APP_HOST"] == "localhost"


def test_cmd_mask_custom_placeholder(capsys):
    with patch("envsnap.cli_mask.load", return_value=_fake_snap()):
        cmd_mask(_ns(placeholder="[HIDDEN]"))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["env"]["APP_SECRET"] == "[HIDDEN]"


def test_cmd_mask_no_auto_skips_secret(capsys):
    with patch("envsnap.cli_mask.load", return_value=_fake_snap()):
        cmd_mask(_ns(no_auto=True, keys=[]))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["env"]["APP_SECRET"] == "abc"


def test_cmd_mask_explicit_key(capsys):
    with patch("envsnap.cli_mask.load", return_value=_fake_snap()):
        cmd_mask(_ns(keys=["APP_HOST"], no_auto=True))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["env"]["APP_HOST"] == "***"


def test_cmd_mask_summary_only(capsys):
    with patch("envsnap.cli_mask.load", return_value=_fake_snap()):
        cmd_mask(_ns(summary=True))
    out = capsys.readouterr().out
    assert "APP_SECRET" in out
    assert "{" not in out


def test_cmd_mask_dotenv_format(capsys):
    with patch("envsnap.cli_mask.load", return_value=_fake_snap()):
        cmd_mask(_ns(format="dotenv"))
    out = capsys.readouterr().out
    assert "APP_SECRET=***" in out


def test_build_parser_defaults():
    p = build_parser()
    args = p.parse_args(["snap.json"])
    assert args.placeholder == "***"
    assert args.format == "json"
    assert not args.no_auto
