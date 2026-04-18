"""Tests for envsnap.baseline_report module."""

from envsnap.baseline_report import format_baseline_diff, baseline_status_line


def _result(added=None, removed=None, changed=None, unchanged=None):
    return {
        "added": added or {},
        "removed": removed or {},
        "changed": changed or {},
        "unchanged": unchanged or {},
    }


def test_format_no_changes():
    out = format_baseline_diff(_result())
    assert "No changes detected" in out


def test_format_shows_added():
    out = format_baseline_diff(_result(added={"NEW": "1"}))
    assert "+ NEW=1" in out
    assert "Added (1)" in out


def test_format_shows_removed():
    out = format_baseline_diff(_result(removed={"OLD": "x"}))
    assert "- OLD=x" in out
    assert "Removed (1)" in out


def test_format_shows_changed():
    out = format_baseline_diff(_result(changed={"PORT": ("8080", "9090")}))
    assert "~ PORT" in out
    assert "8080" in out
    assert "9090" in out


def test_format_total_line():
    r = _result(added={"A": "1"}, removed={"B": "2"}, unchanged={"C": "3"})
    out = format_baseline_diff(r)
    assert "Total changes: 2" in out
    assert "unchanged: 1" in out


def test_format_custom_labels():
    out = format_baseline_diff(_result(), label_a="v1", label_b="v2")
    assert "v1" in out
    assert "v2" in out


def test_status_line_ok():
    assert baseline_status_line(_result()) == "baseline: OK (no changes)"


def test_status_line_changed():
    r = _result(added={"X": "1"}, removed={"Y": "2"}, changed={"Z": ("a", "b")})
    line = baseline_status_line(r)
    assert "CHANGED" in line
    assert "+1" in line
    assert "-1" in line
    assert "~1" in line
