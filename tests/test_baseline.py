"""Tests for envsnap.baseline module."""

import pytest
from pathlib import Path

from envsnap.baseline import (
    set_baseline,
    load_baseline,
    clear_baseline,
    baseline_exists,
    diff_from_baseline,
)


def _snap(env=None, label="test"):
    import time
    return {
        "label": label,
        "timestamp": "2024-01-01T00:00:00",
        "checksum": "abc",
        "env": env or {"APP_ENV": "production", "PORT": "8080"},
    }


@pytest.fixture
def baseline_file(tmp_path):
    return str(tmp_path / "baseline.json")


def test_set_baseline_creates_file(baseline_file):
    snap = _snap()
    path = set_baseline(snap, baseline_file)
    assert Path(baseline_file).exists()


def test_load_baseline_roundtrip(baseline_file):
    snap = _snap()
    set_baseline(snap, baseline_file)
    loaded = load_baseline(baseline_file)
    assert loaded["env"] == snap["env"]
    assert loaded["label"] == snap["label"]


def test_load_baseline_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_baseline(str(tmp_path / "nope.json"))


def test_clear_baseline_returns_true(baseline_file):
    set_baseline(_snap(), baseline_file)
    assert clear_baseline(baseline_file) is True
    assert not Path(baseline_file).exists()


def test_clear_baseline_missing_returns_false(tmp_path):
    assert clear_baseline(str(tmp_path / "ghost.json")) is False


def test_baseline_exists(baseline_file):
    assert not baseline_exists(baseline_file)
    set_baseline(_snap(), baseline_file)
    assert baseline_exists(baseline_file)


def test_diff_from_baseline_detects_added(baseline_file):
    base = _snap({"APP_ENV": "staging"})
    set_baseline(base, baseline_file)
    current = _snap({"APP_ENV": "staging", "NEW_KEY": "value"})
    result = diff_from_baseline(current, baseline_file)
    assert "NEW_KEY" in result["added"]


def test_diff_from_baseline_detects_changed(baseline_file):
    base = _snap({"PORT": "8080"})
    set_baseline(base, baseline_file)
    current = _snap({"PORT": "9090"})
    result = diff_from_baseline(current, baseline_file)
    assert "PORT" in result["changed"]


def test_diff_from_baseline_detects_removed(baseline_file):
    base = _snap({"OLD_KEY": "x", "PORT": "8080"})
    set_baseline(base, baseline_file)
    current = _snap({"PORT": "8080"})
    result = diff_from_baseline(current, baseline_file)
    assert "OLD_KEY" in result["removed"]
