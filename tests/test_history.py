"""Tests for envsnap.history."""

import json
import pytest
from pathlib import Path

from envsnap.history import (
    append_snapshot,
    get_snapshot,
    latest_snapshot,
    list_labels,
    load_history,
    save_history,
)


def _snap(label: str, **env) -> dict:
    return {"label": label, "vars": env, "checksum": "abc"}


@pytest.fixture()
def hist_file(tmp_path):
    return str(tmp_path / "history.json")


def test_load_history_missing_file_returns_empty(hist_file):
    assert load_history(hist_file) == []


def test_save_and_load_roundtrip(hist_file):
    snaps = [_snap("v1"), _snap("v2")]
    save_history(snaps, hist_file)
    assert load_history(hist_file) == snaps


def test_append_snapshot_creates_file(hist_file):
    append_snapshot(_snap("v1"), hist_file)
    assert Path(hist_file).exists()


def test_append_snapshot_accumulates(hist_file):
    append_snapshot(_snap("v1"), hist_file)
    append_snapshot(_snap("v2"), hist_file)
    labels = list_labels(hist_file)
    assert labels == ["v1", "v2"]


def test_get_snapshot_found(hist_file):
    s = _snap("prod")
    append_snapshot(s, hist_file)
    assert get_snapshot("prod", hist_file) == s


def test_get_snapshot_not_found(hist_file):
    append_snapshot(_snap("prod"), hist_file)
    assert get_snapshot("staging", hist_file) is None


def test_latest_snapshot_empty(hist_file):
    assert latest_snapshot(hist_file) is None


def test_latest_snapshot_returns_last(hist_file):
    append_snapshot(_snap("v1"), hist_file)
    append_snapshot(_snap("v2"), hist_file)
    assert latest_snapshot(hist_file)["label"] == "v2"


def test_list_labels_order(hist_file):
    for label in ["a", "b", "c"]:
        append_snapshot(_snap(label), hist_file)
    assert list_labels(hist_file) == ["a", "b", "c"]
