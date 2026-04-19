"""Additional pattern and edge-case tests for env_placeholder."""

import pytest
from envsnap.env_placeholder import is_placeholder, find_placeholders, resolve_placeholders


@pytest.mark.parametrize("value", [
    "<token>",
    "<MY_SECRET_KEY>",
    "${DATABASE_URL}",
    "${X}",
    "CHANGEME",
    "changeme",
    "TODO",
    "todo",
    "REPLACE_ME",
    "replace_me",
    "your-value-here",
    "your_value_here",
])
def test_default_patterns_match(value):
    assert is_placeholder(value), f"Expected {value!r} to be a placeholder"


@pytest.mark.parametrize("value", [
    "postgres://localhost/mydb",
    "true",
    "8080",
    "production",
    "my-real-api-key-abc123",
    "",
    "none",
])
def test_default_patterns_no_match(value):
    assert not is_placeholder(value), f"Expected {value!r} NOT to be a placeholder"


def test_find_placeholders_all_keys():
    snap = {"A": "<a>", "B": "<b>", "C": "real"}
    assert set(find_placeholders(snap)) == {"A", "B"}


def test_resolve_does_not_mutate_original():
    snap = {"X": "CHANGEME"}
    original = dict(snap)
    resolve_placeholders(snap, {"X": "new"})
    assert snap == original


def test_resolve_with_no_placeholders_in_snap():
    snap = {"FOO": "bar", "BAZ": "qux"}
    result = resolve_placeholders(snap, {"FOO": "other"})
    assert result.placeholders == []
    assert result.resolved == []
    assert result.snapshot["FOO"] == "bar"


def test_resolve_partial_overrides():
    snap = {"A": "<a>", "B": "<b>"}
    result = resolve_placeholders(snap, {"A": "real-a"})
    assert "A" in result.resolved
    assert "B" in result.skipped
    assert result.snapshot["A"] == "real-a"
    assert result.snapshot["B"] == "<b>"


def test_resolve_custom_patterns():
    snap = {"KEY": "FILL_THIS", "OTHER": "keep"}
    result = resolve_placeholders(snap, {"KEY": "done"}, patterns=[r"^FILL_THIS$"])
    assert result.snapshot["KEY"] == "done"
    assert result.snapshot["OTHER"] == "keep"
