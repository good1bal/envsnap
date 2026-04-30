"""Tests for ProtectViolation and ProtectResult repr / field contracts."""
from __future__ import annotations

from envsnap.env_protect import ProtectResult, ProtectViolation, protect_summary


def test_protect_violation_attributes():
    v = ProtectViolation(key="MY_KEY", reason="modified")
    assert v.key == "MY_KEY"
    assert v.reason == "modified"


def test_protect_result_defaults():
    r = ProtectResult(env={"A": "1"})
    assert r.protected == []
    assert r.violations == []
    assert r.env == {"A": "1"}


def test_protect_result_with_violations():
    v = ProtectViolation(key="X", reason="deleted")
    r = ProtectResult(env={}, protected=["X"], violations=[v])
    assert len(r.violations) == 1
    assert r.violations[0].reason == "deleted"


def test_protect_summary_counts_line():
    r = ProtectResult(env={}, protected=["A", "B"], violations=[])
    summary = protect_summary(r)
    assert "Protected keys : 2" in summary


def test_protect_summary_violation_detail():
    v = ProtectViolation(key="DB_URL", reason="modified")
    r = ProtectResult(env={}, protected=["DB_URL"], violations=[v])
    summary = protect_summary(r)
    assert "DB_URL" in summary
    assert "modified" in summary


def test_protect_summary_zero_violations_label():
    r = ProtectResult(env={}, protected=["K"], violations=[])
    assert "Violations     : 0" in protect_summary(r)
