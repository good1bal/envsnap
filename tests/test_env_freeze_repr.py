"""Tests for FreezeViolation and FreezeResult repr/attributes."""
from envsnap.env_freeze import FreezeViolation, FreezeResult, freeze_summary


def test_freeze_violation_attributes():
    v = FreezeViolation(key="MY_KEY", reason="value changed from frozen")
    assert v.key == "MY_KEY"
    assert "changed" in v.reason


def test_freeze_result_attributes():
    r = FreezeResult(frozen_keys=["A", "B"], skipped_keys=["C"])
    assert len(r.frozen_keys) == 2
    assert len(r.skipped_keys) == 1


def test_freeze_result_defaults():
    r = FreezeResult()
    assert r.frozen_keys == []
    assert r.skipped_keys == []


def test_freeze_summary_counts():
    r = FreezeResult(frozen_keys=["A", "B", "C"], skipped_keys=[])
    s = freeze_summary(r)
    assert "3" in s


def test_freeze_summary_skipped_count():
    r = FreezeResult(frozen_keys=["A"], skipped_keys=["X", "Y"])
    s = freeze_summary(r)
    assert "2" in s
    assert "Skipped" in s


def test_freeze_violation_equality():
    v1 = FreezeViolation(key="K", reason="r")
    v2 = FreezeViolation(key="K", reason="r")
    assert v1 == v2


def test_freeze_result_frozen_keys_order():
    r = FreezeResult(frozen_keys=["Z", "A", "M"], skipped_keys=[])
    assert r.frozen_keys == ["Z", "A", "M"]
