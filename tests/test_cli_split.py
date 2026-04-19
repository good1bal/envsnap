import json
import pytest
import argparse
from unittest.mock import patch, mock_open
from envsnap.cli_split import cmd_split_prefix, cmd_split_groups, build_parser


_SNAP_JSON = json.dumps({
    "APP_HOST": "localhost",
    "APP_PORT": "8080",
    "DB_HOST": "db.local",
    "SECRET": "s3cr3t",
})

_GROUPS_JSON = json.dumps({"web": ["APP_HOST", "APP_PORT"], "db": ["DB_HOST"]})


def _ns(**kwargs):
    defaults = dict(
        file="snap.json",
        prefixes=["APP_"],
        strip_prefix=False,
        include_remainder=False,
        summary=False,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_split_prefix_output(capsys):
    with patch("builtins.open", mock_open(read_data=_SNAP_JSON)):
        with patch("envsnap.export.from_json", return_value=json.loads(_SNAP_JSON)):
            cmd_split_prefix(_ns())
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "APP_" in data
    assert "APP_HOST" in data["APP_"]


def test_cmd_split_prefix_summary(capsys):
    with patch("builtins.open", mock_open(read_data=_SNAP_JSON)):
        with patch("envsnap.export.from_json", return_value=json.loads(_SNAP_JSON)):
            cmd_split_prefix(_ns(summary=True))
    out = capsys.readouterr().out
    assert "APP_" in out
    assert "remainder" in out


def test_cmd_split_prefix_include_remainder(capsys):
    with patch("builtins.open", mock_open(read_data=_SNAP_JSON)):
        with patch("envsnap.export.from_json", return_value=json.loads(_SNAP_JSON)):
            cmd_split_prefix(_ns(include_remainder=True))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "__remainder__" in data


def test_cmd_split_groups_output(capsys):
    def fake_open(path, *a, **kw):
        if path == "snap.json":
            return mock_open(read_data=_SNAP_JSON)()
        return mock_open(read_data=_GROUPS_JSON)()

    ns = argparse.Namespace(file="snap.json", groups_file="groups.json",
                            include_remainder=False, summary=False)
    with patch("builtins.open", side_effect=fake_open):
        with patch("envsnap.export.from_json", return_value=json.loads(_SNAP_JSON)):
            cmd_split_groups(ns)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "web" in data
    assert "db" in data


def test_build_parser_prefix_command():
    p = build_parser()
    args = p.parse_args(["prefix", "snap.json", "APP_", "DB_"])
    assert args.prefixes == ["APP_", "DB_"]
    assert args.file == "snap.json"


def test_build_parser_groups_command():
    p = build_parser()
    args = p.parse_args(["groups", "snap.json", "groups.json", "--include-remainder"])
    assert args.include_remainder is True
