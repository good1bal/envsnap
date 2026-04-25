"""Tests for envsnap.cli_pivot."""
import json
import argparse
import pytest
from unittest.mock import patch, MagicMock
from envsnap.cli_pivot import cmd_pivot, build_parser


def _ns(**kwargs):
    defaults = {
        "files": [],
        "summary": False,
        "differing_only": False,
        "json": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


_STAGING = {"label": "staging", "env": {"APP_ENV": "staging", "DB": "db-stg"}}
_PROD = {"label": "prod", "env": {"APP_ENV": "prod", "DB": "db-prod", "LOG": "warn"}}


def _make_loader(snaps):
    """Return a side_effect list for from_json calls."""
    import envsnap.export as exp
    return snaps


def test_cmd_pivot_requires_two_files(capsys):
    ns = _ns(files=["only_one.json"])
    with pytest.raises(SystemExit) as exc:
        cmd_pivot(ns)
    assert exc.value.code == 1


def test_cmd_pivot_summary_output(tmp_path, capsys):
    f1 = tmp_path / "staging.json"
    f2 = tmp_path / "prod.json"
    f1.write_text(json.dumps(_STAGING))
    f2.write_text(json.dumps(_PROD))

    with patch("envsnap.cli_pivot.from_json", side_effect=[_STAGING, _PROD]):
        ns = _ns(files=[str(f1), str(f2)], summary=True)
        cmd_pivot(ns)

    out = capsys.readouterr().out
    assert "keys" in out
    assert "snapshots" in out


def test_cmd_pivot_json_output(tmp_path, capsys):
    f1 = tmp_path / "a.json"
    f2 = tmp_path / "b.json"
    f1.write_text("{}")
    f2.write_text("{}")

    with patch("envsnap.cli_pivot.from_json", side_effect=[_STAGING, _PROD]):
        ns = _ns(files=[str(f1), str(f2)], json=True)
        cmd_pivot(ns)

    out = capsys.readouterr().out
    data = json.loads(out)
    assert isinstance(data, list)
    assert all("key" in item and "values" in item for item in data)


def test_cmd_pivot_differing_only(tmp_path, capsys):
    f1 = tmp_path / "a.json"
    f2 = tmp_path / "b.json"
    f1.write_text("{}")
    f2.write_text("{}")

    with patch("envsnap.cli_pivot.from_json", side_effect=[_STAGING, _PROD]):
        ns = _ns(files=[str(f1), str(f2)], differing_only=True)
        cmd_pivot(ns)

    out = capsys.readouterr().out
    # APP_ENV and DB differ; LOG is only in prod (uniform single) -> not shown
    assert "APP_ENV" in out
    assert "DB" in out


def test_build_parser_returns_parser():
    p = build_parser()
    assert isinstance(p, argparse.ArgumentParser)


def test_build_parser_defaults():
    p = build_parser()
    ns = p.parse_args(["a.json", "b.json"])
    assert ns.files == ["a.json", "b.json"]
    assert ns.summary is False
    assert ns.differing_only is False
    assert ns.json is False
