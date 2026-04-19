import argparse
import pytest
from unittest.mock import patch, MagicMock
from envsnap.cli_patch import cmd_patch, _load_ops_from_args, build_parser
from envsnap.env_patch import PatchOperation


def _ns(**kwargs):
    defaults = dict(
        file="snap.json",
        set=None,
        delete=None,
        rename=None,
        output=None,
        strict=False,
        dry_run=False,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_load_ops_set():
    ns = _ns(set=["FOO=bar", "BAZ=qux"])
    ops = _load_ops_from_args(ns)
    assert len(ops) == 2
    assert ops[0].op == "set"
    assert ops[0].key == "FOO"
    assert ops[0].value == "bar"


def test_load_ops_delete():
    ns = _ns(delete=["FOO"])
    ops = _load_ops_from_args(ns)
    assert ops[0].op == "delete"
    assert ops[0].key == "FOO"


def test_load_ops_rename():
    ns = _ns(rename=["OLD:NEW"])
    ops = _load_ops_from_args(ns)
    assert ops[0].op == "rename"
    assert ops[0].key == "OLD"
    assert ops[0].new_key == "NEW"


def test_cmd_patch_dry_run_does_not_save(capsys):
    snap = {"env": {"FOO": "bar"}, "label": "test"}
    ns = _ns(set=["FOO=new"], dry_run=True)
    with patch("envsnap.cli_patch.load", return_value=snap), \
         patch("envsnap.cli_patch.save") as mock_save:
        cmd_patch(ns)
        mock_save.assert_not_called()
    out = capsys.readouterr().out
    assert "Applied" in out


def test_cmd_patch_saves_to_output():
    snap = {"env": {"FOO": "bar"}, "label": "test"}
    ns = _ns(set=["FOO=new"], output="out.json")
    with patch("envsnap.cli_patch.load", return_value=snap), \
         patch("envsnap.cli_patch.save") as mock_save:
        cmd_patch(ns)
        args = mock_save.call_args[0]
        assert args[1] == "out.json"


def test_cmd_patch_saves_to_original_when_no_output():
    snap = {"env": {"FOO": "bar"}, "label": "test"}
    ns = _ns(set=["FOO=new"])
    with patch("envsnap.cli_patch.load", return_value=snap), \
         patch("envsnap.cli_patch.save") as mock_save:
        cmd_patch(ns)
        args = mock_save.call_args[0]
        assert args[1] == "snap.json"


def test_build_parser_returns_parser():
    p = build_parser()
    assert isinstance(p, argparse.ArgumentParser)
