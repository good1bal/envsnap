"""Tests for envsnap.env_defaults."""
import pytest
from envsnap.env_defaults import (
    apply_defaults,
    missing_keys,
    defaults_summary,
    DefaultApplyResult,
)


def _snap(env: dict) -> dict:
    return {"label": "test", "env": env}


def test_apply_defaults_fills_missing_keys():
    snap = _snap({"A": "1"})
    result = apply_defaults(snap, {"B": "2", "C": "3"})
    assert result.snapshot["env"]["B"] == "2"
    assert result.snapshot["env"]["C"] == "3"
    assert result.applied == {"B": "2", "C": "3"}
    assert result.skipped == []


def test_apply_defaults_skips_existing_keys():
    snap = _snap({"A": "1"})
    result = apply_defaults(snap, {"A": "99"})
    assert result.snapshot["env"]["A"] == "1"
    assert result.applied == {}
    assert "A" in result.skipped


def test_apply_defaults_overwrite_flag():
    snap = _snap({"A": "1"})
    result = apply_defaults(snap, {"A": "99"}, overwrite=True)
    assert result.snapshot["env"]["A"] == "99"
    assert result.applied == {"A": "99"}
    assert result.skipped == []


def test_apply_defaults_empty_defaults():
    snap = _snap({"A": "1"})
    result = apply_defaults(snap, {})
    assert result.applied == {}
    assert result.skipped == []
    assert result.snapshot["env"] == {"A": "1"}


def test_apply_defaults_empty_snapshot():
    snap = _snap({})
    result = apply_defaults(snap, {"X": "hello"})
    assert result.snapshot["env"]["X"] == "hello"
    assert result.applied == {"X": "hello"}


def test_apply_defaults_preserves_original_snapshot():
    snap = _snap({"A": "1"})
    apply_defaults(snap, {"B": "2"})
    assert "B" not in snap["env"]


def test_missing_keys_returns_absent_keys():
    snap = _snap({"A": "1", "B": "2"})
    result = missing_keys(snap, {"A": "x", "C": "y"})
    assert result == ["C"]


def test_missing_keys_all_present():
    snap = _snap({"A": "1"})
    assert missing_keys(snap, {"A": "1"}) == []


def test_missing_keys_empty_snapshot():
    snap = _snap({})
    assert missing_keys(snap, {"A": "1", "B": "2"}) == ["A", "B"]


def test_defaults_summary_applied():
    snap = _snap({})
    result = apply_defaults(snap, {"PORT": "8080"})
    summary = defaults_summary(result)
    assert "Applied" in summary
    assert "PORT=8080" in summary


def test_defaults_summary_skipped():
    snap = _snap({"PORT": "3000"})
    result = apply_defaults(snap, {"PORT": "8080"})
    summary = defaults_summary(result)
    assert "Skipped" in summary
    assert "PORT" in summary


def test_defaults_summary_no_changes():
    snap = _snap({})
    result = apply_defaults(snap, {})
    assert defaults_summary(result) == "No defaults applied."
