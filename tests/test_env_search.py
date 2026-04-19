"""Tests for envsnap.env_search."""
import pytest
from envsnap.env_search import SearchResult, search_by_key, search_by_value, search_snapshots


def _snap(label: str, env: dict) -> dict:
    return {"label": label, "env": env}


SNAPS = [
    _snap("prod", {"DATABASE_URL": "postgres://prod", "SECRET_KEY": "abc123", "PORT": "5432"}),
    _snap("staging", {"DATABASE_URL": "postgres://staging", "DEBUG": "true", "PORT": "8000"}),
]


def test_search_by_key_basic():
    results = search_by_key(SNAPS, "database")
    assert len(results) == 2
    assert all(r.key == "DATABASE_URL" for r in results)


def test_search_by_key_case_sensitive_no_match():
    results = search_by_key(SNAPS, "database", case_sensitive=True)
    assert results == []


def test_search_by_key_case_sensitive_match():
    results = search_by_key(SNAPS, "DATABASE", case_sensitive=True)
    assert len(results) == 2


def test_search_by_key_single_snap():
    results = search_by_key(SNAPS, "debug")
    assert len(results) == 1
    assert results[0].label == "staging"


def test_search_by_value_basic():
    results = search_by_value(SNAPS, "postgres")
    assert len(results) == 2


def test_search_by_value_specific():
    results = search_by_value(SNAPS, "prod")
    assert len(results) == 1
    assert results[0].value == "postgres://prod"


def test_search_by_value_no_match():
    results = search_by_value(SNAPS, "nonexistent")
    assert results == []


def test_search_snapshots_key_only():
    results = search_snapshots(SNAPS, key_pattern="PORT")
    assert len(results) == 2


def test_search_snapshots_value_only():
    results = search_snapshots(SNAPS, value_pattern="true")
    assert len(results) == 1
    assert results[0].key == "DEBUG"


def test_search_snapshots_both_patterns():
    results = search_snapshots(SNAPS, key_pattern="DATABASE", value_pattern="staging")
    assert len(results) == 1
    assert results[0].label == "staging"


def test_search_snapshots_no_patterns_returns_empty():
    results = search_snapshots(SNAPS)
    assert results == []


def test_search_result_repr():
    r = SearchResult(label="prod", key="PORT", value="5432")
    assert "prod" in repr(r)
    assert "PORT" in repr(r)
