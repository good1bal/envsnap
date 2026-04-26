"""Tests for envsnap.validate."""
import pytest
from envsnap.validate import validate, validation_summary


def _snap(env: dict) -> dict:
    return {"label": "test", "env": env, "meta": {}}


def test_valid_snapshot_no_rules():
    result = validate(_snap({"FOO": "bar"}))
    assert result.valid
    assert result.issues == []


def test_required_key_present():
    result = validate(_snap({"FOO": "bar"}), required=["FOO"])
    assert result.valid


def test_required_key_missing():
    result = validate(_snap({"BAR": "baz"}), required=["FOO"])
    assert not result.valid
    assert any(i.key == "FOO" for i in result.errors)


def test_forbidden_key_absent():
    result = validate(_snap({"FOO": "bar"}), forbidden=["SECRET"])
    assert result.valid


def test_forbidden_key_present():
    result = validate(_snap({"SECRET": "x"}), forbidden=["SECRET"])
    assert not result.valid
    assert any(i.key == "SECRET" for i in result.errors)


def test_pattern_match_passes():
    result = validate(_snap({"PORT": "8080"}), patterns={"PORT": r"\d+"})
    assert result.valid


def test_pattern_match_fails():
    result = validate(_snap({"PORT": "abc"}), patterns={"PORT": r"\d+"})
    assert not result.valid
    assert any(i.key == "PORT" for i in result.errors)


def test_pattern_skipped_if_key_absent():
    result = validate(_snap({}), patterns={"PORT": r"\d+"})
    assert result.valid


def test_nonempty_warning_on_empty_value():
    result = validate(_snap({"FOO": ""}), nonempty=["FOO"])
    assert result.valid  # only warning
    assert any(i.key == "FOO" and i.severity == "warning" for i in result.issues)


def test_nonempty_no_warning_when_value_set():
    result = validate(_snap({"FOO": "bar"}), nonempty=["FOO"])
    assert result.warnings == []


def test_validation_summary_ok():
    result = validate(_snap({"FOO": "bar"}))
    assert validation_summary(result) == "OK: snapshot is valid."


def test_validation_summary_invalid():
    result = validate(_snap({}), required=["FOO"])
    summary = validation_summary(result)
    assert "INVALID" in summary
    assert "FOO" in summary


def test_multiple_errors():
    result = validate(_snap({"BAD": "x"}), required=["A", "B"], forbidden=["BAD"])
    assert len(result.errors) == 3


def test_validation_summary_includes_warning_count():
    """Summary for a valid-but-warned result should mention the warning count."""
    result = validate(_snap({"FOO": ""}), nonempty=["FOO"])
    summary = validation_summary(result)
    assert "warning" in summary.lower()
    assert "FOO" in summary
