"""Tests for envsnap.env_prefix_rename."""
import pytest
from envsnap.env_prefix_rename import rename_prefix, prefix_rename_summary


def _snap(**kwargs):
    return {k: str(v) for k, v in kwargs.items()}


def test_rename_prefix_basic():
    snap = _snap(OLD_HOST="localhost", OLD_PORT="5432", UNRELATED="x")
    result = rename_prefix(snap, "OLD_", "NEW_")
    assert "NEW_HOST" in result.snapshot
    assert "NEW_PORT" in result.snapshot
    assert "UNRELATED" in result.snapshot
    assert "OLD_HOST" not in result.snapshot


def test_rename_prefix_values_preserved():
    snap = _snap(OLD_HOST="localhost")
    result = rename_prefix(snap, "OLD_", "NEW_")
    assert result.snapshot["NEW_HOST"] == "localhost"


def test_rename_prefix_tracks_renamed():
    snap = _snap(OLD_A="1", OLD_B="2", KEEP="3")
    result = rename_prefix(snap, "OLD_", "NEW_")
    assert sorted(result.renamed) == ["OLD_A", "OLD_B"]
    assert result.skipped == []


def test_rename_prefix_no_match_leaves_snapshot_unchanged():
    snap = _snap(FOO="bar", BAZ="qux")
    result = rename_prefix(snap, "MISSING_", "X_")
    assert result.snapshot == snap
    assert result.renamed == []


def test_rename_prefix_conflict_skips_by_default():
    # NEW_HOST already exists — should not overwrite
    snap = {"OLD_HOST": "old", "NEW_HOST": "existing"}
    result = rename_prefix(snap, "OLD_", "NEW_")
    assert result.snapshot["NEW_HOST"] == "existing"
    assert result.snapshot["OLD_HOST"] == "old"
    assert "OLD_HOST" in result.skipped


def test_rename_prefix_conflict_overwrite_flag():
    snap = {"OLD_HOST": "new_val", "NEW_HOST": "existing"}
    result = rename_prefix(snap, "OLD_", "NEW_", overwrite=True)
    assert result.snapshot["NEW_HOST"] == "new_val"
    assert "OLD_HOST" not in result.snapshot
    assert result.skipped == []


def test_rename_prefix_empty_prefix_renames_all():
    snap = _snap(A="1", B="2")
    result = rename_prefix(snap, "", "X_")
    assert "X_A" in result.snapshot
    assert "X_B" in result.snapshot
    assert len(result.renamed) == 2


def test_prefix_rename_summary_contains_counts():
    snap = _snap(OLD_A="1", OLD_B="2")
    result = rename_prefix(snap, "OLD_", "NEW_")
    summary = prefix_rename_summary(result)
    assert "Renamed" in summary
    assert "2" in summary
    assert "Skipped" in summary


def test_prefix_rename_summary_lists_skipped():
    snap = {"OLD_X": "v", "NEW_X": "existing"}
    result = rename_prefix(snap, "OLD_", "NEW_")
    summary = prefix_rename_summary(result)
    assert "OLD_X" in summary
