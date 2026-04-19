"""Tests for envsnap.env_placeholder."""

import pytest
from envsnap.env_placeholder import (
    is_placeholder,
    find_placeholders,
    resolve_placeholders,
    placeholder_summary,
    PlaceholderResult,
)


def _snap(**kwargs):
    return {k: v for k, v in kwargs.items()}


# --- is_placeholder ---

def test_is_placeholder_angle_brackets():
    assert is_placeholder("<your-token>")


def test_is_placeholder_dollar_brace():
    assert is_placeholder("${MY_SECRET}")


def test_is_placeholder_changeme():
    assert is_placeholder("CHANGEME")


def test_is_placeholder_todo():
    assert is_placeholder("TODO")


def test_is_placeholder_real_value_false():
    assert not is_placeholder("postgres://localhost/db")


def test_is_placeholder_custom_pattern():
    assert is_placeholder("FILL_THIS", patterns=[r"^FILL_THIS$"])


def test_is_placeholder_custom_pattern_no_match():
    assert not is_placeholder("hello", patterns=[r"^FILL_THIS$"])


# --- find_placeholders ---

def test_find_placeholders_returns_matching_keys():
    snap = _snap(DB_URL="<your-db-url>", APP_KEY="real-key", SECRET="CHANGEME")
    found = find_placeholders(snap)
    assert set(found) == {"DB_URL", "SECRET"}


def test_find_placeholders_empty_snap():
    assert find_placeholders({}) == []


def test_find_placeholders_none_match():
    snap = _snap(FOO="bar", BAZ="qux")
    assert find_placeholders(snap) == []


# --- resolve_placeholders ---

def test_resolve_fills_known_placeholders():
    snap = _snap(DB_URL="<your-db-url>", PORT="5432")
    result = resolve_placeholders(snap, {"DB_URL": "postgres://localhost/db"})
    assert result.snapshot["DB_URL"] == "postgres://localhost/db"
    assert result.snapshot["PORT"] == "5432"
    assert "DB_URL" in result.resolved


def test_resolve_skips_unresolved_placeholders():
    snap = _snap(SECRET="CHANGEME")
    result = resolve_placeholders(snap, {})
    assert result.snapshot["SECRET"] == "CHANGEME"
    assert "SECRET" in result.skipped


def test_resolve_returns_placeholder_result_type():
    snap = _snap(X="TODO")
    result = resolve_placeholders(snap, {"X": "done"})
    assert isinstance(result, PlaceholderResult)


def test_resolve_repr_contains_counts():
    snap = _snap(A="<a>", B="real")
    result = resolve_placeholders(snap, {"A": "val"})
    r = repr(result)
    assert "placeholders=1" in r
    assert "resolved=1" in r


# --- placeholder_summary ---

def test_placeholder_summary_shows_resolved():
    snap = _snap(A="<a>")
    result = resolve_placeholders(snap, {"A": "v"})
    s = placeholder_summary(result)
    assert "Resolved" in s
    assert "A" in s


def test_placeholder_summary_shows_unresolved():
    snap = _snap(B="CHANGEME")
    result = resolve_placeholders(snap, {})
    s = placeholder_summary(result)
    assert "Unresolved" in s
    assert "B" in s
