"""Tests for envsnap.filter module."""
import pytest
from envsnap.filter import (
    exclude_by_prefix,
    filter_by_pattern,
    filter_by_prefix,
    mask_values,
    select_keys,
)

SAMPLE: dict = {
    "APP_HOST": "localhost",
    "APP_PORT": "8080",
    "DB_URL": "postgres://localhost/db",
    "SECRET_KEY": "s3cr3t",
    "TOKEN_GITHUB": "ghp_abc",
    "PATH": "/usr/bin",
}


def test_filter_by_prefix_single():
    result = filter_by_prefix(SAMPLE, ["APP_"])
    assert set(result.keys()) == {"APP_HOST", "APP_PORT"}


def test_filter_by_prefix_multiple():
    result = filter_by_prefix(SAMPLE, ["APP_", "DB_"])
    assert "APP_HOST" in result and "DB_URL" in result
    assert "PATH" not in result


def test_filter_by_prefix_empty_returns_all():
    result = filter_by_prefix(SAMPLE, [])
    assert result == SAMPLE


def test_exclude_by_prefix():
    result = exclude_by_prefix(SAMPLE, ["APP_", "DB_"])
    assert "APP_HOST" not in result
    assert "DB_URL" not in result
    assert "PATH" in result


def test_exclude_by_prefix_empty_returns_all():
    result = exclude_by_prefix(SAMPLE, [])
    assert result == SAMPLE


def test_filter_by_pattern():
    result = filter_by_pattern(SAMPLE, r"^APP_")
    assert set(result.keys()) == {"APP_HOST", "APP_PORT"}


def test_filter_by_pattern_no_match():
    result = filter_by_pattern(SAMPLE, r"^NONEXISTENT")
    assert result == {}


def test_mask_values_defaults():
    result = mask_values(SAMPLE)
    assert result["SECRET_KEY"] == "***"
    assert result["TOKEN_GITHUB"] == "***"
    assert result["APP_HOST"] == "localhost"


def test_mask_values_custom_prefixes():
    result = mask_values(SAMPLE, sensitive_prefixes=["DB_"], mask="REDACTED")
    assert result["DB_URL"] == "REDACTED"
    assert result["SECRET_KEY"] == "s3cr3t"


def test_select_keys_present():
    result = select_keys(SAMPLE, ["APP_HOST", "PATH"])
    assert result == {"APP_HOST": "localhost", "PATH": "/usr/bin"}


def test_select_keys_missing_ignored():
    result = select_keys(SAMPLE, ["APP_HOST", "MISSING_KEY"])
    assert "MISSING_KEY" not in result
    assert "APP_HOST" in result
