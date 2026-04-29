"""Tests for envsnap.env_rollback."""
from __future__ import annotations

import pytest

from envsnap.env_rollback import rollback, rollback_summary, RollbackResult


def _snap(label: str, env: dict) -> dict:
    return {"label": label, "env": env, "meta": {}}


# ---------------------------------------------------------------------------
# rollback – full revert
# ---------------------------------------------------------------------------

def test_rollback_restores_changed_value():
    current = _snap("new", {"A": "2", "B": "keep"})
    target = _snap("old", {"A": "1", "B": "keep"})
    result = rollback(current, target)
    assert result.reverted["A"] == "1"
    assert "A" in result.keys_restored


def test_rollback_removes_key_added_since_target():
    current = _snap("new", {"A": "1", "EXTRA": "x"})
    target = _snap("old", {"A": "1"})
    result = rollback(current, target)
    assert "EXTRA" not in result.reverted
    assert "EXTRA" in result.keys_removed


def test_rollback_restores_key_deleted_since_target():
    current = _snap("new", {"A": "1"})
    target = _snap("old", {"A": "1", "GONE": "old_val"})
    result = rollback(current, target)
    assert result.reverted["GONE"] == "old_val"
    assert "GONE" in result.keys_restored


def test_rollback_unchanged_keys_tracked():
    current = _snap("new", {"A": "same", "B": "2"})
    target = _snap("old", {"A": "same", "B": "1"})
    result = rollback(current, target)
    assert "A" in result.keys_unchanged
    assert "B" in result.keys_restored


def test_rollback_identical_snapshots_no_changes():
    snap = _snap("x", {"A": "1", "B": "2"})
    result = rollback(snap, snap)
    assert result.keys_restored == []
    assert result.keys_removed == []
    assert len(result.keys_unchanged) == 2


# ---------------------------------------------------------------------------
# rollback – partial (keys filter)
# ---------------------------------------------------------------------------

def test_rollback_partial_only_affects_specified_keys():
    current = _snap("new", {"A": "2", "B": "2"})
    target = _snap("old", {"A": "1", "B": "1"})
    result = rollback(current, target, keys=["A"])
    assert result.reverted["A"] == "1"
    assert result.reverted["B"] == "2"  # untouched


def test_rollback_partial_missing_key_in_current_skipped():
    current = _snap("new", {"A": "2"})
    target = _snap("old", {"A": "1", "B": "1"})
    result = rollback(current, target, keys=["A", "B"])
    assert result.reverted["B"] == "1"
    assert "B" in result.keys_restored


# ---------------------------------------------------------------------------
# RollbackResult helpers
# ---------------------------------------------------------------------------

def test_rollback_result_original_unchanged():
    current = _snap("new", {"A": "2"})
    target = _snap("old", {"A": "1"})
    result = rollback(current, target)
    assert result.original["A"] == "2"


def test_rollback_diff_reflects_changes():
    current = _snap("new", {"A": "2", "EXTRA": "x"})
    target = _snap("old", {"A": "1"})
    result = rollback(current, target)
    assert len(result.diff.changed) > 0 or len(result.diff.removed) > 0


# ---------------------------------------------------------------------------
# rollback_summary
# ---------------------------------------------------------------------------

def test_rollback_summary_contains_counts():
    current = _snap("new", {"A": "2", "B": "keep", "C": "extra"})
    target = _snap("old", {"A": "1", "B": "keep"})
    result = rollback(current, target)
    summary = rollback_summary(result)
    assert "Restored" in summary
    assert "Removed" in summary
    assert "Unchanged" in summary
