"""Tests for envsnap.env_transform."""
import pytest
from envsnap.env_transform import (
    apply_transform,
    uppercase_values,
    lowercase_values,
    strip_values,
    transform_summary,
    TransformResult,
)


def _snap(**kw) -> dict:
    return dict(kw)


def test_apply_transform_all_keys():
    snap = _snap(FOO="hello", BAR="world")
    result = apply_transform(snap, str.upper)
    assert result.transformed == {"FOO": "HELLO", "BAR": "WORLD"}
    assert set(result.applied) == {"FOO", "BAR"}
    assert result.skipped == []


def test_apply_transform_selected_keys():
    snap = _snap(FOO="hello", BAR="world")
    result = apply_transform(snap, str.upper, keys=["FOO"])
    assert result.transformed["FOO"] == "HELLO"
    assert result.transformed["BAR"] == "world"
    assert result.applied == ["FOO"]


def test_apply_transform_missing_key_skipped():
    snap = _snap(FOO="hello")
    result = apply_transform(snap, str.upper, keys=["FOO", "MISSING"])
    assert "MISSING" in result.skipped
    assert "FOO" in result.applied


def test_apply_transform_exception_causes_skip():
    def boom(v):
        raise ValueError("nope")

    snap = _snap(FOO="hello")
    result = apply_transform(snap, boom, keys=["FOO"])
    assert "FOO" in result.skipped
    assert result.applied == []


def test_uppercase_values():
    snap = _snap(A="abc", B="xyz")
    result = uppercase_values(snap)
    assert result.transformed == {"A": "ABC", "B": "XYZ"}


def test_lowercase_values():
    snap = _snap(A="ABC", B="XYZ")
    result = lowercase_values(snap)
    assert result.transformed == {"A": "abc", "B": "xyz"}


def test_strip_values():
    snap = _snap(A="  hello  ", B="\tworld\n")
    result = strip_values(snap)
    assert result.transformed["A"] == "hello"
    assert result.transformed["B"] == "world"


def test_original_unchanged():
    snap = _snap(FOO="hello")
    result = uppercase_values(snap)
    assert result.original["FOO"] == "hello"


def test_transform_summary_no_skipped():
    snap = _snap(FOO="hello")
    result = uppercase_values(snap)
    summary = transform_summary(result)
    assert "Applied" in summary
    assert "1" in summary


def test_transform_summary_with_skipped():
    snap = _snap(FOO="hello")
    result = apply_transform(snap, str.upper, keys=["FOO", "BAR"])
    summary = transform_summary(result)
    assert "BAR" in summary


def test_repr():
    snap = _snap(A="x")
    result = uppercase_values(snap)
    assert "TransformResult" in repr(result)
