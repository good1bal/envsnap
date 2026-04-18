"""Tests for envsnap.timeline."""

import pytest

from envsnap.history import append_snapshot, save_history
from envsnap.timeline import build_timeline, timeline_summary


def _snap(label: str, **vars_) -> dict:
    from envsnap.snapshot import _checksum
    return {"label": label, "vars": vars_, "checksum": _checksum(vars_)}


@pytest.fixture()
def hist_file(tmp_path):
    return str(tmp_path / "history.json")


def test_build_timeline_empty_history(hist_file):
    assert build_timeline(hist_file) == []


def test_build_timeline_single_snapshot(hist_file):
    append_snapshot(_snap("v1", A="1"), hist_file)
    assert build_timeline(hist_file) == []


def test_build_timeline_two_snapshots(hist_file):
    append_snapshot(_snap("v1", A="1"), hist_file)
    append_snapshot(_snap("v2", A="1", B="2"), hist_file)
    tl = build_timeline(hist_file)
    assert len(tl) == 1
    assert tl[0]["from"] == "v1"
    assert tl[0]["to"] == "v2"
    assert "B" in tl[0]["diff"].added


def test_build_timeline_three_snapshots(hist_file):
    append_snapshot(_snap("v1", A="1"), hist_file)
    append_snapshot(_snap("v2", A="2"), hist_file)
    append_snapshot(_snap("v3", A="2", C="3"), hist_file)
    tl = build_timeline(hist_file)
    assert len(tl) == 2
    assert tl[1]["from"] == "v2"
    assert tl[1]["to"] == "v3"


def test_timeline_summary_returns_strings(hist_file):
    append_snapshot(_snap("v1", X="a"), hist_file)
    append_snapshot(_snap("v2", X="b"), hist_file)
    summaries = timeline_summary(hist_file)
    assert len(summaries) == 1
    assert "v1" in summaries[0]
    assert "v2" in summaries[0]


def test_timeline_summary_empty(hist_file):
    assert timeline_summary(hist_file) == []
