"""Tests for envsnap.cli_diff_score."""
import json
import argparse
import pytest

from envsnap.cli_diff_score import cmd_score, build_parser
from envsnap.export import to_json


def _snap(label: str, env: dict) -> dict:
    return {"label": label, "env": env, "checksum": "abc"}


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {"json": False, "verbose": False, "fail_below": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture()
def snap_files(tmp_path):
    a = _snap("prod", {"DB": "postgres", "PORT": "5432"})
    b = _snap("staging", {"DB": "postgres", "PORT": "3306", "NEW": "val"})
    fa = tmp_path / "a.json"
    fb = tmp_path / "b.json"
    fa.write_text(to_json(a))
    fb.write_text(to_json(b))
    return str(fa), str(fb)


# ---------------------------------------------------------------------------
# cmd_score
# ---------------------------------------------------------------------------

def test_cmd_score_prints_summary(snap_files, capsys):
    fa, fb = snap_files
    ns = _ns(file_a=fa, file_b=fb)
    cmd_score(ns)
    out = capsys.readouterr().out
    assert "prod" in out
    assert "staging" in out


def test_cmd_score_json_output(snap_files, capsys):
    fa, fb = snap_files
    ns = _ns(file_a=fa, file_b=fb, json=True)
    cmd_score(ns)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "similarity" in data
    assert "divergence" in data
    assert "breakdown" in data
    assert data["label_a"] == "prod"
    assert data["label_b"] == "staging"


def test_cmd_score_verbose_shows_counts(snap_files, capsys):
    fa, fb = snap_files
    ns = _ns(file_a=fa, file_b=fb, verbose=True)
    cmd_score(ns)
    out = capsys.readouterr().out
    assert "total keys" in out
    assert "added" in out
    assert "removed" in out


def test_cmd_score_missing_file_exits_one(tmp_path):
    fa = str(tmp_path / "missing_a.json")
    fb = str(tmp_path / "missing_b.json")
    ns = _ns(file_a=fa, file_b=fb)
    with pytest.raises(SystemExit) as exc:
        cmd_score(ns)
    assert exc.value.code == 1


def test_cmd_score_fail_below_exits_two_when_low(snap_files):
    fa, fb = snap_files
    ns = _ns(file_a=fa, file_b=fb, fail_below=0.999)
    with pytest.raises(SystemExit) as exc:
        cmd_score(ns)
    assert exc.value.code == 2


def test_cmd_score_fail_below_no_exit_when_above(snap_files):
    fa, fb = snap_files
    # identical snapshots → similarity == 1.0
    ns = _ns(file_a=fa, file_b=fa, fail_below=0.5)
    cmd_score(ns)  # should not raise


def test_build_parser_returns_parser():
    p = build_parser()
    assert isinstance(p, argparse.ArgumentParser)


def test_build_parser_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    p = build_parser(parent=sub)
    assert p is not None
