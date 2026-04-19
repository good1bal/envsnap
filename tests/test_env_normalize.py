"""Tests for envsnap.env_normalize."""
import pytest
from envsnap.env_normalize import (
    normalize_keys,
    normalize_values,
    normalize_summary,
    NormalizeResult,
)


def _snap(**kw) -> dict:
    return {k: str(v) for k, v in kw.items()}


# --- normalize_keys ---

def test_normalize_keys_uppercase():
    snap = _snap(path="/usr/bin", home="/root")
    result = normalize_keys(snap)
    assert "PATH" in result.normalized
    assert "HOME" in result.normalized


def test_normalize_keys_no_change_when_already_upper():
    snap = _snap(PATH="/usr/bin")
    result = normalize_keys(snap)
    assert result.renamed == {}


def test_normalize_keys_renamed_tracks_changes():
    snap = {"myKey": "val", "OTHER": "x"}
    result = normalize_keys(snap)
    assert "myKey" in result.renamed
    assert result.renamed["myKey"] == "MYKEY"
    assert "OTHER" not in result.renamed


def test_normalize_keys_custom_fn():
    snap = {"FOO": "1", "BAR": "2"}
    result = normalize_keys(snap, fn=str.lower)
    assert "foo" in result.normalized
    assert "bar" in result.normalized


def test_normalize_keys_preserves_values():
    snap = {"key": "hello"}
    result = normalize_keys(snap)
    assert result.normalized["KEY"] == "hello"


# --- normalize_values ---

def test_normalize_values_strips_whitespace():
    snap = {"A": "  hello  ", "B": "world"}
    result = normalize_values(snap)
    assert result.normalized["A"] == "hello"
    assert result.normalized["B"] == "world"


def test_normalize_values_transformed_only_changed():
    snap = {"A": "  hi  ", "B": "clean"}
    result = normalize_values(snap)
    assert "A" in result.transformed
    assert "B" not in result.transformed


def test_normalize_values_restricted_keys():
    snap = {"A": "  x  ", "B": "  y  "}
    result = normalize_values(snap, keys=["A"])
    assert result.normalized["A"] == "x"
    assert result.normalized["B"] == "  y  "


def test_normalize_values_missing_key_skipped():
    snap = {"A": "val"}
    result = normalize_values(snap, keys=["A", "MISSING"])
    assert "MISSING" not in result.normalized


def test_normalize_values_custom_fn():
    snap = {"A": "hello"}
    result = normalize_values(snap, fn=str.upper)
    assert result.normalized["A"] == "HELLO"


# --- normalize_summary ---

def test_normalize_summary_contains_counts():
    snap = {"myKey": "  val  "}
    result = normalize_keys(snap)
    summary = normalize_summary(result)
    assert "Renamed keys" in summary
    assert "myKey" in summary


def test_repr_normalize_result():
    r = NormalizeResult(original={}, normalized={}, renamed={"a": "A"}, transformed={})
    assert "renamed=1" in repr(r)
