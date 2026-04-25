"""Tests for envsnap.env_required."""
import pytest

from envsnap.env_required import (
    RequiredCheckResult,
    check_required,
    required_summary,
)


def _snap(**kwargs: str):
    return {"label": "test", "captured_at": "2024-01-01T00:00:00", **kwargs}


def test_check_required_all_present():
    snap = _snap(FOO="1", BAR="2")
    result = check_required(snap, ["FOO", "BAR"])
    assert result.satisfied
    assert set(result.present) == {"FOO", "BAR"}
    assert result.missing == []


def test_check_required_some_missing():
    snap = _snap(FOO="1")
    result = check_required(snap, ["FOO", "BAR", "BAZ"])
    assert not result.satisfied
    assert "FOO" in result.present
    assert set(result.missing) == {"BAR", "BAZ"}


def test_check_required_empty_required_list():
    snap = _snap(FOO="1")
    result = check_required(snap, [])
    assert result.satisfied
    assert result.present == []
    assert result.missing == []


def test_check_required_apply_defaults_fills_missing():
    snap = _snap(FOO="1")
    result = check_required(
        snap,
        ["FOO", "BAR"],
        defaults={"BAR": "default_bar"},
        apply_defaults=True,
    )
    assert result.satisfied
    assert "BAR" in result.present
    assert result.defaults_applied == {"BAR": "default_bar"}
    assert result.missing == []


def test_check_required_apply_defaults_false_does_not_fill():
    snap = _snap(FOO="1")
    result = check_required(
        snap,
        ["FOO", "BAR"],
        defaults={"BAR": "default_bar"},
        apply_defaults=False,
    )
    assert not result.satisfied
    assert "BAR" in result.missing
    assert result.defaults_applied == {}


def test_check_required_no_defaults_provided():
    snap = _snap()
    result = check_required(snap, ["MISSING"])
    assert not result.satisfied
    assert "MISSING" in result.missing


def test_check_required_does_not_mutate_snap():
    snap = _snap(FOO="1")
    original_keys = set(snap.keys())
    check_required(snap, ["FOO", "BAR"], defaults={"BAR": "x"}, apply_defaults=True)
    assert set(snap.keys()) == original_keys


def test_required_summary_all_present():
    result = RequiredCheckResult(present=["A", "B"], missing=[])
    summary = required_summary(result)
    assert "Present" in summary
    assert "Missing" in summary
    assert "2" in summary


def test_required_summary_with_missing():
    result = RequiredCheckResult(present=["A"], missing=["B", "C"])
    summary = required_summary(result)
    assert "B" in summary
    assert "C" in summary


def test_required_summary_with_defaults_applied():
    result = RequiredCheckResult(
        present=["A", "B"],
        missing=[],
        defaults_applied={"B": "fallback"},
    )
    summary = required_summary(result)
    assert "Defaulted" in summary
    assert "fallback" in summary
