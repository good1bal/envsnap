"""Tests for envsnap.cli_placeholder."""

import argparse
import pytest
from unittest.mock import patch, MagicMock

from envsnap.cli_placeholder import cmd_find, cmd_resolve, build_parser


def _ns(**kwargs):
    defaults = {"file": None, "override": None, "override_json": None, "out": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


FAKE_SNAP = {"DB_URL": "<your-db-url>", "PORT": "5432", "SECRET": "CHANGEME"}


def test_cmd_find_no_placeholders(capsys):
    clean = {"PORT": "5432"}
    with patch("envsnap.cli_placeholder.capture", return_value=clean):
        cmd_find(_ns())
    out = capsys.readouterr().out
    assert "No placeholders" in out


def test_cmd_find_with_placeholders(capsys):
    with patch("envsnap.cli_placeholder.capture", return_value=FAKE_SNAP):
        cmd_find(_ns())
    out = capsys.readouterr().out
    assert "DB_URL" in out
    assert "SECRET" in out


def test_cmd_find_from_file(capsys, tmp_path):
    snap_file = str(tmp_path / "snap.json")
    with patch("envsnap.cli_placeholder.load", return_value=FAKE_SNAP) as mock_load:
        cmd_find(_ns(file=snap_file))
        mock_load.assert_called_once_with(snap_file)
    out = capsys.readouterr().out
    assert "placeholder" in out


def test_cmd_resolve_fills_value(capsys):
    with patch("envsnap.cli_placeholder.capture", return_value=dict(FAKE_SNAP)):
        cmd_resolve(_ns(override=["DB_URL=postgres://localhost/db"]))
    out = capsys.readouterr().out
    assert "Resolved" in out


def test_cmd_resolve_invalid_override_exits():
    with patch("envsnap.cli_placeholder.capture", return_value=dict(FAKE_SNAP)):
        with pytest.raises(SystemExit):
            cmd_resolve(_ns(override=["BADFORMAT"]))


def test_cmd_resolve_invalid_json_exits():
    with patch("envsnap.cli_placeholder.capture", return_value=dict(FAKE_SNAP)):
        with pytest.raises(SystemExit):
            cmd_resolve(_ns(override_json="{not valid json}"))


def test_cmd_resolve_saves_output(tmp_path, capsys):
    out_file = str(tmp_path / "resolved.json")
    with patch("envsnap.cli_placeholder.capture", return_value=dict(FAKE_SNAP)), \
         patch("envsnap.cli_placeholder.save") as mock_save:
        cmd_resolve(_ns(override=["DB_URL=real"], out=out_file))
        mock_save.assert_called_once()
    out = capsys.readouterr().out
    assert "Saved" in out


def test_build_parser_returns_parser():
    p = build_parser()
    assert p is not None


def test_build_parser_find_subcommand():
    p = build_parser()
    args = p.parse_args(["find"])
    assert args.command == "find"


def test_build_parser_resolve_subcommand():
    p = build_parser()
    args = p.parse_args(["resolve", "--override", "X=1"])
    assert args.command == "resolve"
    assert args.override == ["X=1"]
