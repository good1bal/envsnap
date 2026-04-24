"""Tests for envsnap.env_sanitize."""
from __future__ import annotations

import pytest

from envsnap.env_sanitize import (
    SanitizeResult,
    sanitize_keys,
    sanitize_values,
    sanitize_summary,
)


def _snap(**kwargs) -> dict:
    return dict(kwargs)


# ---------------------------------------------------------------------------
# sanitize_keys
# ---------------------------------------------------------------------------

def test_sanitize_keys_already_valid():
    snap = _snap(FOO="bar", BAZ_QUX="1")
    result = sanitize_keys(snap)
    assert result.env == snap
    assert result.renamed_keys == {}
    assert result.dropped_keys == []


def test_sanitize_keys_lowercased_to_upper():
    snap = _snap(foo="bar")
    result = sanitize_keys(snap)
    assert "FOO" in result.env
    assert result.renamed_keys == {"foo": "FOO"}


def test_sanitize_keys_invalid_chars_replaced():
    snap = {"my-key": "val"}
    result = sanitize_keys(snap)
    assert "MY_KEY" in result.env
    assert result.renamed_keys == {"my-key": "MY_KEY"}


def test_sanitize_keys_drops_all_underscore_result():
    snap = {"---": "val"}
    result = sanitize_keys(snap)
    assert result.env == {}
    assert "---" in result.dropped_keys


def test_sanitize_keys_custom_key_fn():
    snap = _snap(FOO="1", BAR="2")
    # Drop BAR, keep FOO unchanged
    result = sanitize_keys(snap, key_fn=lambda k: k if k == "FOO" else None)
    assert result.env == {"FOO": "1"}
    assert "BAR" in result.dropped_keys


def test_sanitize_keys_preserves_values():
    snap = {"hello world": "some_value"}
    result = sanitize_keys(snap)
    assert result.env["HELLO_WORLD"] == "some_value"


# ---------------------------------------------------------------------------
# sanitize_values
# ---------------------------------------------------------------------------

def test_sanitize_values_no_control_chars():
    snap = _snap(FOO="clean", BAR="also clean")
    result = sanitize_values(snap)
    assert result.env == snap
    assert result.cleaned_values == []


def test_sanitize_values_strips_null_bytes():
    snap = {"FOO": "val\x00ue"}
    result = sanitize_values(snap)
    assert result.env["FOO"] == "value"
    assert "FOO" in result.cleaned_values


def test_sanitize_values_strips_newline_in_value():
    snap = {"KEY": "line1\nline2"}
    result = sanitize_values(snap)
    assert result.env["KEY"] == "line1line2"
    assert "KEY" in result.cleaned_values


def test_sanitize_values_custom_fn():
    snap = _snap(FOO="  spaced  ")
    result = sanitize_values(snap, value_fn=str.strip)
    assert result.env["FOO"] == "spaced"
    assert "FOO" in result.cleaned_values


def test_sanitize_values_preserves_keys():
    snap = _snap(A="x", B="y")
    result = sanitize_values(snap)
    assert set(result.env.keys()) == {"A", "B"}


# ---------------------------------------------------------------------------
# sanitize_summary
# ---------------------------------------------------------------------------

def test_sanitize_summary_no_changes():
    result = SanitizeResult(env={"A": "1", "B": "2"})
    summary = sanitize_summary(result)
    assert "2 keys" in summary
    assert "renamed" not in summary
    assert "dropped" not in summary


def test_sanitize_summary_with_changes():
    result = SanitizeResult(
        env={"FOO": "bar"},
        renamed_keys={"foo": "FOO"},
        dropped_keys=["---"],
        cleaned_values=["FOO"],
    )
    summary = sanitize_summary(result)
    assert "1 renamed" in summary
    assert "1 dropped" in summary
    assert "1 values cleaned" in summary
