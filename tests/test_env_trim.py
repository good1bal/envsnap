"""Tests for envsnap.env_trim."""
import pytest
from envsnap.env_trim import trim_keys, trim_values, trim_summary, TrimResult


def _snap(**kw):
    return dict(kw)


# --- trim_keys ---

def test_trim_keys_strips_whitespace():
    snap = {"  FOO  ": "bar", "BAZ": "qux"}
    result = trim_keys(snap)
    assert "FOO" in result.snapshot
    assert "BAZ" in result.snapshot
    assert result.trimmed_keys == ["  FOO  "]


def test_trim_keys_no_change_when_clean():
    snap = _snap(A="1", B="2")
    result = trim_keys(snap)
    assert result.trimmed_keys == []
    assert result.snapshot == snap


def test_trim_keys_custom_fn():
    snap = {"foo": "val", "bar": "val2"}
    result = trim_keys(snap, fn=str.upper)
    assert "FOO" in result.snapshot
    assert "BAR" in result.snapshot
    assert set(result.trimmed_keys) == {"foo", "bar"}


def test_trim_keys_preserves_values():
    snap = {"  KEY  ": "hello world"}
    result = trim_keys(snap)
    assert result.snapshot["KEY"] == "hello world"


# --- trim_values ---

def test_trim_values_strips_whitespace():
    snap = _snap(A="  hello  ", B="world")
    result = trim_values(snap)
    assert result.snapshot["A"] == "hello"
    assert result.snapshot["B"] == "world"
    assert result.trimmed_values == ["A"]


def test_trim_values_no_change_when_clean():
    snap = _snap(X="clean", Y="also_clean")
    result = trim_values(snap)
    assert result.trimmed_values == []


def test_trim_values_limited_to_keys():
    snap = _snap(A="  a  ", B="  b  ")
    result = trim_values(snap, keys=["A"])
    assert result.snapshot["A"] == "a"
    assert result.snapshot["B"] == "  b  "
    assert result.trimmed_values == ["A"]


def test_trim_values_skips_missing_key():
    snap = _snap(A="value")
    result = trim_values(snap, keys=["A", "MISSING"])
    assert "MISSING" not in result.snapshot
    assert result.trimmed_values == []


def test_trim_values_custom_fn():
    snap = _snap(PATH="/usr/local/bin")
    result = trim_values(snap, fn=lambda v: v.replace("/usr", ""))
    assert result.snapshot["PATH"] == "/local/bin"


# --- TrimResult repr ---

def test_trim_result_repr():
    r = TrimResult(snapshot={}, trimmed_keys=["A"], trimmed_values=["B", "C"])
    text = repr(r)
    assert "keys_trimmed=1" in text
    assert "values_trimmed=2" in text


# --- trim_summary ---

def test_trim_summary_includes_counts():
    snap = {"  K  ": "  v  "}
    r1 = trim_keys(snap)
    r2 = trim_values(r1.snapshot)
    combined = TrimResult(
        snapshot=r2.snapshot,
        trimmed_keys=r1.trimmed_keys,
        trimmed_values=r2.trimmed_values,
    )
    summary = trim_summary(combined)
    assert "Keys trimmed" in summary
    assert "Values trimmed" in summary


def test_trim_summary_lists_affected_keys():
    r = TrimResult(snapshot={}, trimmed_keys=["FOO"], trimmed_values=["BAR"])
    summary = trim_summary(r)
    assert "FOO" in summary
    assert "BAR" in summary
