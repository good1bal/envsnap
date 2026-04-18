"""Tests for envsnap.env_rename."""

import pytest

from envsnap.env_rename import (
    RenameConflict,
    rename_key,
    rename_keys,
    rename_summary,
)


def _snap(**kwargs):
    return {"label": "test", "env": dict(kwargs)}


def test_rename_key_basic():
    snap = _snap(FOO="1", BAR="2")
    result = rename_key(snap, "FOO", "FOO_NEW")
    assert "FOO_NEW" in result["env"]
    assert result["env"]["FOO_NEW"] == "1"
    assert "FOO" not in result["env"]


def test_rename_key_preserves_other_keys():
    snap = _snap(FOO="1", BAR="2")
    result = rename_key(snap, "FOO", "FOO_NEW")
    assert result["env"]["BAR"] == "2"


def test_rename_key_missing_raises():
    snap = _snap(FOO="1")
    with pytest.raises(KeyError):
        rename_key(snap, "MISSING", "NEW")


def test_rename_key_conflict_raises_by_default():
    snap = _snap(FOO="1", BAR="2")
    with pytest.raises(RenameConflict):
        rename_key(snap, "FOO", "BAR")


def test_rename_key_conflict_overwrite():
    snap = _snap(FOO="1", BAR="2")
    result = rename_key(snap, "FOO", "BAR", overwrite=True)
    assert result["env"]["BAR"] == "1"
    assert "FOO" not in result["env"]


def test_rename_key_does_not_mutate_original():
    snap = _snap(FOO="1")
    rename_key(snap, "FOO", "FOO2")
    assert "FOO" in snap["env"]


def test_rename_keys_multiple():
    snap = _snap(A="1", B="2", C="3")
    result = rename_keys(snap, {"A": "AA", "B": "BB"})
    assert "AA" in result["env"]
    assert "BB" in result["env"]
    assert "A" not in result["env"]
    assert "B" not in result["env"]
    assert result["env"]["C"] == "3"


def test_rename_keys_empty_mapping():
    snap = _snap(A="1")
    result = rename_keys(snap, {})
    assert result["env"] == snap["env"]


def test_rename_summary_empty():
    assert rename_summary({}) == "No renames."


def test_rename_summary_non_empty():
    summary = rename_summary({"OLD": "NEW"})
    assert "OLD" in summary
    assert "NEW" in summary
    assert "->" in summary
