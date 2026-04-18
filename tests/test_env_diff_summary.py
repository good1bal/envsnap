import pytest
from envsnap.env_diff_summary import (
    compute_stats,
    build_diff_summary,
    format_diff_summary,
    DiffStats,
)
from envsnap.diff import compare


def _snap(label, env):
    return {"label": label, "env": env, "checksum": "x"}


def test_compute_stats_all_unchanged():
    snap_a = _snap("a", {"FOO": "1", "BAR": "2"})
    snap_b = _snap("b", {"FOO": "1", "BAR": "2"})
    result = compare(snap_a, snap_b)
    stats = compute_stats(result)
    assert stats.added == 0
    assert stats.removed == 0
    assert stats.changed == 0
    assert stats.unchanged == 2


def test_compute_stats_added():
    snap_a = _snap("a", {})
    snap_b = _snap("b", {"NEW": "1"})
    result = compare(snap_a, snap_b)
    stats = compute_stats(result)
    assert stats.added == 1
    assert stats.total_changes == 1


def test_compute_stats_removed():
    snap_a = _snap("a", {"OLD": "1"})
    snap_b = _snap("b", {})
    result = compare(snap_a, snap_b)
    stats = compute_stats(result)
    assert stats.removed == 1


def test_compute_stats_changed():
    snap_a = _snap("a", {"K": "v1"})
    snap_b = _snap("b", {"K": "v2"})
    result = compare(snap_a, snap_b)
    stats = compute_stats(result)
    assert stats.changed == 1


def test_build_diff_summary_labels():
    snap_a = _snap("prod", {"A": "1"})
    snap_b = _snap("staging", {"A": "1", "B": "2"})
    report = build_diff_summary(snap_a, snap_b)
    assert report.label_a == "prod"
    assert report.label_b == "staging"
    assert "B" in report.added_keys


def test_build_diff_summary_changed_keys_sorted():
    snap_a = _snap("a", {"Z": "1", "A": "1"})
    snap_b = _snap("b", {"Z": "2", "A": "2"})
    report = build_diff_summary(snap_a, snap_b)
    assert report.changed_keys == sorted(report.changed_keys)


def test_format_diff_summary_contains_labels():
    snap_a = _snap("env1", {"X": "1"})
    snap_b = _snap("env2", {"X": "2"})
    report = build_diff_summary(snap_a, snap_b)
    text = format_diff_summary(report)
    assert "env1" in text
    assert "env2" in text
    assert "Changed" in text


def test_format_diff_summary_no_changes():
    snap_a = _snap("a", {"K": "v"})
    snap_b = _snap("b", {"K": "v"})
    report = build_diff_summary(snap_a, snap_b)
    text = format_diff_summary(report)
    assert "Unchanged: 1" in text
    assert "+" not in text
