"""Tests for envsnap.redact module."""
import pytest
from envsnap.redact import is_sensitive, redact, split_sensitive

ENV = {
    "APP_NAME": "myapp",
    "DATABASE_PASSWORD": "hunter2",
    "GITHUB_TOKEN": "ghp_xyz",
    "PORT": "3000",
    "SECRET_KEY": "abc123",
    "AUTH_HEADER": "Bearer tok",
}


@pytest.mark.parametrize(
    "key,expected",
    [
        ("SECRET_KEY", True),
        ("DATABASE_PASSWORD", True),
        ("GITHUB_TOKEN", True),
        ("AUTH_HEADER", True),
        ("APP_NAME", False),
        ("PORT", False),
    ],
)
def test_is_sensitive(key, expected):
    assert is_sensitive(key) is expected


def test_redact_replaces_sensitive():
    result = redact(ENV)
    assert result["DATABASE_PASSWORD"] == "<redacted>"
    assert result["GITHUB_TOKEN"] == "<redacted>"
    assert result["SECRET_KEY"] == "<redacted>"


def test_redact_preserves_safe():
    result = redact(ENV)
    assert result["APP_NAME"] == "myapp"
    assert result["PORT"] == "3000"


def test_redact_custom_placeholder():
    result = redact(ENV, placeholder="HIDDEN")
    assert result["SECRET_KEY"] == "HIDDEN"


def test_redact_custom_substrings():
    result = redact(ENV, substrings=["PORT"])
    assert result["PORT"] == "<redacted>"
    assert result["SECRET_KEY"] == "abc123"


def test_split_sensitive_counts():
    safe, sensitive = split_sensitive(ENV)
    assert "APP_NAME" in safe
    assert "PORT" in safe
    assert "DATABASE_PASSWORD" in sensitive
    assert "GITHUB_TOKEN" in sensitive


def test_split_sensitive_no_overlap():
    safe, sensitive = split_sensitive(ENV)
    assert set(safe.keys()).isdisjoint(set(sensitive.keys()))


def test_split_sensitive_union_equals_original():
    safe, sensitive = split_sensitive(ENV)
    merged = {**safe, **sensitive}
    assert merged == ENV
