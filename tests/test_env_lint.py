"""Tests for envsnap.env_lint."""
import pytest
from envsnap.env_lint import lint_snapshot, lint_summary, LintIssue, LintResult


def _snap(env: dict) -> dict:
    return {"label": "test", "env": env}


def test_lint_clean_snapshot_no_issues():
    result = lint_snapshot(_snap({"DATABASE_URL": "postgres://localhost/db"}))
    assert result.passed
    assert result.issues == []


def test_lint_lowercase_key_warns():
    result = lint_snapshot(_snap({"database_url": "value"}))
    assert any(i.key == "database_url" for i in result.warnings)


def test_lint_allow_lowercase_suppresses_warning():
    result = lint_snapshot(_snap({"database_url": "value"}), allow_lowercase=True)
    assert result.passed
    assert result.issues == []


def test_lint_double_underscore_warns():
    result = lint_snapshot(_snap({"MY__KEY": "value"}))
    assert any("double underscore" in i.message for i in result.warnings)


def test_lint_value_too_long_warns():
    result = lint_snapshot(_snap({"KEY": "x" * 50}), max_value_length=10)
    assert any("exceeds max length" in i.message for i in result.warnings)


def test_lint_value_within_limit_no_issue():
    result = lint_snapshot(_snap({"KEY": "short"}), max_value_length=10)
    assert result.passed


def test_lint_forbidden_pattern_is_error():
    result = lint_snapshot(
        _snap({"SECRET": "password123"}),
        forbidden_patterns=[r"password"]
    )
    assert not result.passed
    assert any(i.severity == "error" for i in result.issues)


def test_lint_no_forbidden_pattern_match():
    result = lint_snapshot(
        _snap({"SECRET": "tok_abc"}),
        forbidden_patterns=[r"password"]
    )
    assert result.passed


def test_lint_result_errors_and_warnings_split():
    result = lint_snapshot(
        _snap({"bad_key": "password123"}),
        forbidden_patterns=[r"password"]
    )
    assert len(result.errors) == 1
    assert len(result.warnings) >= 1


def test_lint_summary_no_issues():
    result = LintResult()
    assert lint_summary(result) == "lint: no issues found"


def test_lint_summary_with_issues():
    result = lint_snapshot(_snap({"bad_key": "value"}))
    summary = lint_summary(result)
    assert "warning" in summary
    assert "bad_key" in summary


def test_lint_empty_snapshot():
    result = lint_snapshot(_snap({}))
    assert result.passed
    assert result.issues == []
