"""Tests for envsnap.diff module."""

import pytest

from envsnap.diff import compare, summary


def _snap(env: dict) -> dict:
    return {"env": env}


def test_added_keys():
    result = compare(_snap({"A": "1"}), _snap({"A": "1", "B": "2"}))
    assert result["added"] == {"B": "2"}
    assert result["removed"] == {}


def test_removed_keys():
    result = compare(_snap({"A": "1", "B": "2"}), _snap({"A": "1"}))
    assert result["removed"] == {"B": "2"}
    assert result["added"] == {}


def test_changed_keys():
    result = compare(_snap({"A": "old"}), _snap({"A": "new"}))
    assert result["changed"] == {"A": {"before": "old", "after": "new"}}


def test_unchanged_keys():
    result = compare(_snap({"A": "1"}), _snap({"A": "1"}))
    assert result["unchanged"] == {"A": "1"}
    assert result["changed"] == {}


def test_empty_snapshots():
    result = compare(_snap({}), _snap({}))
    assert result["added"] == {}
    assert result["removed"] == {}
    assert result["changed"] == {}
    assert result["unchanged"] == {}


def test_summary_format():
    result = compare(
        _snap({"A": "1", "B": "2"}),
        _snap({"A": "changed", "C": "3"}),
    )
    text = summary(result)
    assert "Added" in text
    assert "Removed" in text
    assert "Changed" in text
