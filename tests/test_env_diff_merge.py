"""Tests for envsnap.env_diff_merge."""
import pytest

from envsnap.env_diff_merge import (
    DiffMergeResult,
    diff_merge,
    diff_merge_summary,
)


def _snap(**kwargs):
    return {k: str(v) for k, v in kwargs.items()}


# ---------------------------------------------------------------------------
# diff_merge
# ---------------------------------------------------------------------------

def test_diff_merge_returns_diff_merge_result():
    result = diff_merge(_snap(A="1"), _snap(A="1"), _snap(A="1"))
    assert isinstance(result, DiffMergeResult)


def test_diff_merge_applies_changed_key_from_source():
    base = _snap(A="1", B="2")
    source = _snap(A="1", B="99")  # B changed in source
    target = _snap(A="1", B="2")  # target still at base
    result = diff_merge(base, source, target)
    assert result.env["B"] == "99"
    assert "B" in result.applied


def test_diff_merge_applies_added_key_from_source():
    base = _snap(A="1")
    source = _snap(A="1", NEW="hello")
    target = _snap(A="1")
    result = diff_merge(base, source, target)
    assert result.env["NEW"] == "hello"
    assert "NEW" in result.applied


def test_diff_merge_skips_unchanged_key_when_overwrite_false():
    base = _snap(A="1", B="2")
    source = _snap(A="1", B="99")  # B changed in source
    target = _snap(A="1", B="2")  # target still at base
    result = diff_merge(base, source, target, overwrite_unchanged=False)
    # B is in target already and overwrite_unchanged=False → skipped
    assert result.env["B"] == "2"
    assert "B" in result.skipped


def test_diff_merge_detects_conflict():
    base = _snap(A="1")
    source = _snap(A="source_val")
    target = _snap(A="target_val")
    result = diff_merge(base, source, target)
    assert "A" in result.conflicts
    # target value wins by default
    assert result.env["A"] == "target_val"


def test_diff_merge_conflict_in_skipped():
    base = _snap(A="1")
    source = _snap(A="s")
    target = _snap(A="t")
    result = diff_merge(base, source, target)
    assert "A" in result.skipped


def test_diff_merge_raise_on_conflict():
    base = _snap(A="1")
    source = _snap(A="s")
    target = _snap(A="t")
    with pytest.raises(ValueError, match="Merge conflict on key"):
        diff_merge(base, source, target, raise_on_conflict=True)


def test_diff_merge_no_changes_returns_target_unchanged():
    base = _snap(A="1", B="2")
    source = _snap(A="1", B="2")
    target = _snap(A="1", B="2")
    result = diff_merge(base, source, target)
    assert result.env == target
    assert result.applied == []
    assert result.skipped == []
    assert result.conflicts == []


def test_diff_merge_preserves_target_only_keys():
    base = _snap(A="1")
    source = _snap(A="1")
    target = _snap(A="1", EXTRA="only_in_target")
    result = diff_merge(base, source, target)
    assert result.env["EXTRA"] == "only_in_target"


# ---------------------------------------------------------------------------
# diff_merge_summary
# ---------------------------------------------------------------------------

def test_diff_merge_summary_no_conflicts():
    result = DiffMergeResult(
        env={"A": "1"},
        applied=["A"],
        skipped=[],
        conflicts=[],
    )
    summary = diff_merge_summary(result)
    assert "Applied" in summary
    assert "1" in summary
    assert "Conflict" not in summary or "0" in summary


def test_diff_merge_summary_with_conflicts():
    result = DiffMergeResult(
        env={"A": "t"},
        applied=[],
        skipped=["A"],
        conflicts=["A"],
    )
    summary = diff_merge_summary(result)
    assert "A" in summary
    assert "Conflict" in summary
