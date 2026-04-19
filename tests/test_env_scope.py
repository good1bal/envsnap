"""Tests for envsnap.env_scope."""
import pytest
from envsnap.env_scope import (
    assign_scope,
    filter_by_scope,
    get_scope,
    scope_summary,
    remove_scope,
    SCOPE_KEY,
)


def _snap(**kwargs) -> dict:
    return {"label": "test", "env": kwargs, **kwargs}


BASE = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "prod", "SECRET": "s3cr3t"}


def test_assign_scope_adds_scope_key():
    snap = assign_scope(BASE, ["DB_HOST", "DB_PORT"], "database")
    assert SCOPE_KEY in snap


def test_assign_scope_maps_keys():
    snap = assign_scope(BASE, ["DB_HOST", "DB_PORT"], "database")
    assert snap[SCOPE_KEY]["DB_HOST"] == "database"
    assert snap[SCOPE_KEY]["DB_PORT"] == "database"


def test_assign_scope_ignores_missing_keys():
    snap = assign_scope(BASE, ["NONEXISTENT"], "x")
    assert "NONEXISTENT" not in snap.get(SCOPE_KEY, {})


def test_assign_scope_preserves_existing_scopes():
    snap = assign_scope(BASE, ["DB_HOST"], "database")
    snap2 = assign_scope(snap, ["APP_ENV"], "app")
    assert snap2[SCOPE_KEY]["DB_HOST"] == "database"
    assert snap2[SCOPE_KEY]["APP_ENV"] == "app"


def test_assign_scope_does_not_mutate_original():
    original = dict(BASE)
    assign_scope(original, ["DB_HOST"], "database")
    assert SCOPE_KEY not in original


def test_filter_by_scope_returns_matching_keys():
    snap = assign_scope(BASE, ["DB_HOST", "DB_PORT"], "database")
    result = filter_by_scope(snap, "database")
    assert set(result.keys()) == {"DB_HOST", "DB_PORT"}


def test_filter_by_scope_excludes_other_scopes():
    snap = assign_scope(BASE, ["APP_ENV"], "app")
    snap = assign_scope(snap, ["DB_HOST"], "database")
    result = filter_by_scope(snap, "app")
    assert "DB_HOST" not in result


def test_filter_by_scope_empty_when_no_match():
    snap = assign_scope(BASE, ["DB_HOST"], "database")
    result = filter_by_scope(snap, "nonexistent")
    assert result == {}


def test_get_scope_returns_assigned_scope():
    snap = assign_scope(BASE, ["SECRET"], "secrets")
    assert get_scope(snap, "SECRET") == "secrets"


def test_get_scope_returns_none_for_unassigned():
    assert get_scope(BASE, "DB_HOST") is None


def test_scope_summary_groups_keys_by_scope():
    snap = assign_scope(BASE, ["DB_HOST", "DB_PORT"], "database")
    snap = assign_scope(snap, ["APP_ENV"], "app")
    summary = scope_summary(snap)
    assert set(summary["database"]) == {"DB_HOST", "DB_PORT"}
    assert summary["app"] == ["APP_ENV"]


def test_scope_summary_empty_when_no_scopes():
    assert scope_summary(BASE) == {}


def test_remove_scope_deletes_assignment():
    snap = assign_scope(BASE, ["DB_HOST"], "database")
    snap2 = remove_scope(snap, "DB_HOST")
    assert get_scope(snap2, "DB_HOST") is None


def test_remove_scope_preserves_other_assignments():
    snap = assign_scope(BASE, ["DB_HOST", "DB_PORT"], "database")
    snap2 = remove_scope(snap, "DB_HOST")
    assert get_scope(snap2, "DB_PORT") == "database"
