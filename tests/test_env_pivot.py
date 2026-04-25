"""Tests for envsnap.env_pivot."""
import pytest
from envsnap.env_pivot import PivotRow, PivotTable, build_pivot, pivot_summary


def _snaps():
    return {
        "staging": {"APP_ENV": "staging", "DB_HOST": "db-stg", "DEBUG": "true"},
        "prod": {"APP_ENV": "prod", "DB_HOST": "db-prod", "LOG_LEVEL": "warn"},
    }


def test_build_pivot_returns_pivot_table():
    table = build_pivot(_snaps())
    assert isinstance(table, PivotTable)


def test_build_pivot_labels_preserved():
    table = build_pivot(_snaps())
    assert table.labels == ["staging", "prod"]


def test_build_pivot_all_keys_present():
    table = build_pivot(_snaps())
    keys = [r.key for r in table.rows]
    assert "APP_ENV" in keys
    assert "DB_HOST" in keys
    assert "DEBUG" in keys
    assert "LOG_LEVEL" in keys


def test_build_pivot_keys_sorted():
    table = build_pivot(_snaps())
    keys = [r.key for r in table.rows]
    assert keys == sorted(keys)


def test_pivot_row_missing_value_is_none():
    table = build_pivot(_snaps())
    debug_row = next(r for r in table.rows if r.key == "DEBUG")
    assert debug_row.values["staging"] == "true"
    assert debug_row.values["prod"] is None


def test_pivot_row_is_uniform_same_value():
    row = PivotRow(key="K", values={"a": "v", "b": "v"})
    assert row.is_uniform() is True


def test_pivot_row_is_not_uniform_different_values():
    row = PivotRow(key="K", values={"a": "v1", "b": "v2"})
    assert row.is_uniform() is False


def test_pivot_row_missing_treated_as_non_uniform():
    row = PivotRow(key="K", values={"a": "v1", "b": None})
    # None excluded from uniform check — only present values compared
    assert row.is_uniform() is True  # only one non-None value


def test_pivot_row_missing_in():
    row = PivotRow(key="K", values={"a": "v", "b": None, "c": None})
    assert row.missing_in() == ["b", "c"]


def test_pivot_table_len():
    table = build_pivot(_snaps())
    assert len(table) == 4


def test_pivot_table_uniform_rows():
    table = build_pivot(_snaps())
    uniform_keys = [r.key for r in table.uniform_rows()]
    # APP_ENV differs staging/prod -> not uniform; DB_HOST differs -> not uniform
    # DEBUG only in staging (one value) -> uniform; LOG_LEVEL only in prod -> uniform
    assert "DEBUG" in uniform_keys
    assert "LOG_LEVEL" in uniform_keys


def test_pivot_table_differing_rows():
    table = build_pivot(_snaps())
    differing_keys = [r.key for r in table.differing_rows()]
    assert "APP_ENV" in differing_keys
    assert "DB_HOST" in differing_keys


def test_pivot_summary_format():
    table = build_pivot(_snaps())
    s = pivot_summary(table)
    assert "4 keys" in s
    assert "2 snapshots" in s


def test_build_pivot_empty():
    table = build_pivot({})
    assert len(table) == 0
    assert table.labels == []


def test_build_pivot_single_snapshot():
    table = build_pivot({"only": {"A": "1", "B": "2"}})
    assert len(table) == 2
    assert all(r.is_uniform() for r in table.rows)
