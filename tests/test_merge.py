"""Tests for envsnap.merge."""

import pytest

from envsnap.merge import MergeConflict, merge, merge_labels


def _snap(label: str, variables: dict) -> dict:
    from envsnap.snapshot import _checksum
    return {"label": label, "variables": variables, "checksum": _checksum(variables)}


def test_merge_single_snapshot():
    snap = _snap("prod", {"HOST": "localhost", "PORT": "8080"})
    result = merge(snap, label="merged")
    assert result["variables"] == {"HOST": "localhost", "PORT": "8080"}
    assert result["label"] == "merged"


def test_merge_two_disjoint_snapshots():
    a = _snap("a", {"FOO": "1"})
    b = _snap("b", {"BAR": "2"})
    result = merge(a, b)
    assert result["variables"] == {"FOO": "1", "BAR": "2"}


def test_merge_identical_keys_no_conflict():
    a = _snap("a", {"FOO": "same"})
    b = _snap("b", {"FOO": "same"})
    result = merge(a, b)
    assert result["variables"]["FOO"] == "same"


def test_merge_conflict_raises_by_default():
    a = _snap("a", {"FOO": "1"})
    b = _snap("b", {"FOO": "2"})
    with pytest.raises(MergeConflict, match="FOO"):
        merge(a, b)


def test_merge_conflict_first():
    a = _snap("a", {"FOO": "first"})
    b = _snap("b", {"FOO": "last"})
    result = merge(a, b, on_conflict="first")
    assert result["variables"]["FOO"] == "first"


def test_merge_conflict_last():
    a = _snap("a", {"FOO": "first"})
    b = _snap("b", {"FOO": "last"})
    result = merge(a, b, on_conflict="last")
    assert result["variables"]["FOO"] == "last"


def test_merge_checksum_present():
    snap = _snap("x", {"A": "1"})
    result = merge(snap)
    assert "checksum" in result
    assert isinstance(result["checksum"], str)


def test_merge_no_snapshots_raises():
    with pytest.raises(ValueError):
        merge()


def test_merge_labels_returns_all_labels():
    a = _snap("alpha", {})
    b = _snap("beta", {})
    assert merge_labels(a, b) == ["alpha", "beta"]
