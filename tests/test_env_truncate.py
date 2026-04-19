"""Tests for envsnap.env_truncate."""
import pytest
from envsnap.env_truncate import truncate_values, truncate_summary, TruncateResult


def _snap(**kwargs) -> dict:
    return {k: v for k, v in kwargs.items()}


def test_truncate_short_values_unchanged():
    snap = _snap(FOO="hi", BAR="ok")
    result = truncate_values(snap, max_length=10)
    assert result.snapshot == snap
    assert result.truncated_keys == []


def test_truncate_long_value():
    snap = _snap(FOO="a" * 20)
    result = truncate_values(snap, max_length=10)
    assert len(result.snapshot["FOO"]) == 10
    assert result.snapshot["FOO"].endswith("...")
    assert "FOO" in result.truncated_keys


def test_truncate_preserves_other_keys():
    snap = _snap(FOO="a" * 20, BAR="short")
    result = truncate_values(snap, max_length=10)
    assert result.snapshot["BAR"] == "short"
    assert "BAR" not in result.truncated_keys


def test_truncate_custom_suffix():
    snap = _snap(KEY="hello world")
    result = truncate_values(snap, max_length=8, suffix="--")
    assert result.snapshot["KEY"] == "hello w--"[:8]
    assert result.snapshot["KEY"].endswith("--")


def test_truncate_selected_keys_only():
    snap = _snap(A="a" * 20, B="b" * 20)
    result = truncate_values(snap, max_length=5, keys=["A"])
    assert "A" in result.truncated_keys
    assert "B" not in result.truncated_keys
    assert result.snapshot["B"] == "b" * 20


def test_truncate_original_lengths_recorded():
    snap = _snap(X="x" * 50)
    result = truncate_values(snap, max_length=10)
    assert result.original_lengths["X"] == 50


def test_truncate_max_length_equals_value_length_no_change():
    snap = _snap(KEY="exact")
    result = truncate_values(snap, max_length=5)
    assert result.snapshot["KEY"] == "exact"
    assert "KEY" not in result.truncated_keys


def test_truncate_invalid_max_length_raises():
    with pytest.raises(ValueError):
        truncate_values({"K": "v"}, max_length=2, suffix="...")


def test_truncate_empty_snapshot():
    result = truncate_values({}, max_length=10)
    assert result.snapshot == {}
    assert result.truncated_keys == []


def test_summary_no_truncations():
    result = TruncateResult(snapshot={"A": "hi"}, truncated_keys=[], original_lengths={})
    assert truncate_summary(result) == "No values truncated."


def test_summary_with_truncations():
    snap = _snap(LONG="x" * 50)
    result = truncate_values(snap, max_length=10)
    summary = truncate_summary(result)
    assert "LONG" in summary
    assert "50" in summary


def test_repr_includes_count():
    result = TruncateResult(
        snapshot={},
        truncated_keys=["A", "B"],
        original_lengths={"A": 20, "B": 30},
    )
    assert "2" in repr(result)
