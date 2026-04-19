import json
import pytest
from unittest.mock import patch, mock_open, MagicMock
from envsnap.cli_union import cmd_union, build_parser


def _ns(**kwargs):
    defaults = dict(
        files=[],
        strategy="first",
        output=None,
        label="union",
        summary=False,
    )
    defaults.update(kwargs)
    import argparse
    return argparse.Namespace(**defaults)


def _snap_json(label, **kwargs):
    return json.dumps({"label": label, "env": kwargs})


def test_cmd_union_missing_file_exits(tmp_path, capsys):
    ns = _ns(files=[str(tmp_path / "missing.json")])
    with pytest.raises(SystemExit) as exc:
        cmd_union(ns)
    assert exc.value.code == 1


def test_cmd_union_prints_merged_keys(tmp_path, capsys):
    f1 = tmp_path / "a.json"
    f2 = tmp_path / "b.json"
    f1.write_text(_snap_json("a", FOO="1"))
    f2.write_text(_snap_json("b", BAR="2"))
    ns = _ns(files=[str(f1), str(f2)])
    cmd_union(ns)
    out = capsys.readouterr().out
    assert "FOO=1" in out
    assert "BAR=2" in out


def test_cmd_union_summary_flag(tmp_path, capsys):
    f1 = tmp_path / "a.json"
    f1.write_text(_snap_json("a", X="1"))
    ns = _ns(files=[str(f1)], summary=True)
    cmd_union(ns)
    out = capsys.readouterr().out
    assert "Total keys" in out


def test_cmd_union_error_strategy_exits(tmp_path, capsys):
    f1 = tmp_path / "a.json"
    f2 = tmp_path / "b.json"
    f1.write_text(_snap_json("a", FOO="1"))
    f2.write_text(_snap_json("b", FOO="2"))
    ns = _ns(files=[str(f1), str(f2)], strategy="error")
    with pytest.raises(SystemExit) as exc:
        cmd_union(ns)
    assert exc.value.code == 2


def test_cmd_union_writes_output_file(tmp_path):
    f1 = tmp_path / "a.json"
    f1.write_text(_snap_json("a", FOO="1"))
    out_file = tmp_path / "out.json"
    ns = _ns(files=[str(f1)], output=str(out_file))
    cmd_union(ns)
    data = json.loads(out_file.read_text())
    assert data["env"]["FOO"] == "1"


def test_build_parser_returns_parser():
    p = build_parser()
    assert p is not None
