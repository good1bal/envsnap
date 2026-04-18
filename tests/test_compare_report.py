"""Tests for compare_report and report_format."""

import pytest
from envsnap.compare_report import build_report, CompareReport
from envsnap.report_format import format_report


def _snap(label: str, vars: dict) -> dict:
    return {"label": label, "vars": vars}


SNAP_A = _snap("prod-v1", {"HOST": "localhost", "PORT": "8080", "SECRET_KEY": "abc123"})
SNAP_B = _snap("prod-v2", {"HOST": "remotehost", "PORT": "8080", "DEBUG": "true"})


def test_build_report_returns_compare_report():
    report = build_report(SNAP_A, SNAP_B)
    assert isinstance(report, CompareReport)


def test_labels_set_correctly():
    report = build_report(SNAP_A, SNAP_B)
    assert report.label_a == "prod-v1"
    assert report.label_b == "prod-v2"


def test_added_keys_detected():
    report = build_report(SNAP_A, SNAP_B)
    keys = [e.key for e in report.by_status("added")]
    assert "DEBUG" in keys


def test_removed_keys_detected():
    report = build_report(SNAP_A, SNAP_B)
    keys = [e.key for e in report.by_status("removed")]
    assert "SECRET_KEY" in keys


def test_changed_keys_detected():
    report = build_report(SNAP_A, SNAP_B)
    keys = [e.key for e in report.by_status("changed")]
    assert "HOST" in keys


def test_sensitive_values_redacted():
    report = build_report(SNAP_A, SNAP_B, redact_sensitive=True)
    removed = {e.key: e for e in report.by_status("removed")}
    assert removed["SECRET_KEY"].old_value != "abc123"


def test_sensitive_values_not_redacted_when_disabled():
    report = build_report(SNAP_A, SNAP_B, redact_sensitive=False)
    removed = {e.key: e for e in report.by_status("removed")}
    assert removed["SECRET_KEY"].old_value == "abc123"


def test_unchanged_excluded_by_default():
    report = build_report(SNAP_A, SNAP_B)
    assert report.by_status("unchanged") == []


def test_unchanged_included_when_requested():
    report = build_report(SNAP_A, SNAP_B, include_unchanged=True)
    keys = [e.key for e in report.by_status("unchanged")]
    assert "PORT" in keys


def test_has_changes_true():
    report = build_report(SNAP_A, SNAP_B)
    assert report.has_changes is True


def test_has_changes_false_for_identical():
    snap = _snap("x", {"A": "1"})
    report = build_report(snap, snap)
    assert report.has_changes is False


def test_format_report_contains_labels():
    report = build_report(SNAP_A, SNAP_B)
    output = format_report(report)
    assert "prod-v1" in output
    assert "prod-v2" in output


def test_format_report_summary_line():
    report = build_report(SNAP_A, SNAP_B)
    output = format_report(report)
    assert "Summary:" in output


def test_format_report_no_changes_message():
    snap = _snap("x", {"A": "1"})
    report = build_report(snap, snap)
    output = format_report(report)
    assert "No changes detected" in output
