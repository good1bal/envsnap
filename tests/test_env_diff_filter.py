"""Tests for envsnap.env_diff_filter."""
import pytest

from envsnap.diff import compare
from envsnap.env_diff_filter import (
    FilteredDiff,
    changes_only,
    filter_diff,
    filter_diff_summary,
)


def _result():
    a = {"HOST": "localhost", "PORT": "5432", "OLD": "gone", "SAME": "x"}
    b = {"HOST": "prod.db", "PORT": "5432", "NEW": "here", "SAME": "x"}
    return compare(a, b)


def test_filter_diff_returns_filtered_diff():
    fd = filter_diff(_result())
    assert isinstance(fd, FilteredDiff)


def test_filter_no_criteria_returns_all_entries():
    fd = filter_diff(_result())
    assert len(fd) == 4  # added, removed, changed, unchanged


def test_filter_by_status_added():
    fd = filter_diff(_result(), statuses=["added"])
    assert all(e["status"] == "added" for e in fd.entries)
    assert any(e["key"] == "NEW" for e in fd.entries)


def test_filter_by_status_removed():
    fd = filter_diff(_result(), statuses=["removed"])
    assert len(fd) == 1
    assert fd.entries[0]["key"] == "OLD"


def test_filter_by_status_changed():
    fd = filter_diff(_result(), statuses=["changed"])
    assert len(fd) == 1
    assert fd.entries[0]["key"] == "HOST"


def test_filter_by_multiple_statuses():
    fd = filter_diff(_result(), statuses=["added", "removed"])
    statuses = {e["status"] for e in fd.entries}
    assert statuses == {"added", "removed"}


def test_filter_by_key_pattern():
    fd = filter_diff(_result(), key_pattern=r"^(HOST|PORT)$")
    keys = {e["key"] for e in fd.entries}
    assert keys == {"HOST", "PORT"}


def test_filter_by_predicate():
    fd = filter_diff(_result(), predicate=lambda e: e["after"] is not None)
    assert all(e["after"] is not None for e in fd.entries)


def test_changes_only_excludes_unchanged():
    fd = changes_only(_result())
    assert all(e["status"] != "unchanged" for e in fd.entries)
    assert len(fd) == 3


def test_filter_diff_summary_counts():
    fd = changes_only(_result())
    s = filter_diff_summary(fd)
    assert "added" in s
    assert "removed" in s
    assert "changed" in s


def test_filter_diff_summary_no_entries():
    fd = filter_diff(_result(), statuses=["added"], key_pattern="NOMATCH")
    assert filter_diff_summary(fd) == "no entries"
