"""Tests for envsnap.env_freeze."""
import json
import pytest

from envsnap.env_freeze import (
    FreezeViolation,
    FreezeResult,
    load_frozen,
    save_frozen,
    freeze_keys,
    unfreeze_keys,
    check_freeze,
    freeze_summary,
)


def _snap(env: dict) -> dict:
    return {"label": "test", "env": env}


@pytest.fixture()
def store(tmp_path):
    return str(tmp_path)


def test_load_frozen_missing_file_returns_empty(store):
    assert load_frozen(store) == {}


def test_save_and_load_roundtrip(store):
    data = {"API_KEY": "abc123", "DB_PASS": "secret"}
    save_frozen(data, store)
    assert load_frozen(store) == data


def test_freeze_keys_basic(store):
    snap = _snap({"API_KEY": "abc", "DB_HOST": "localhost"})
    result = freeze_keys(snap, keys=["API_KEY"], store_dir=store)
    assert "API_KEY" in result.frozen_keys
    assert result.skipped_keys == []
    assert load_frozen(store)["API_KEY"] == "abc"


def test_freeze_all_keys_when_none_specified(store):
    snap = _snap({"A": "1", "B": "2"})
    result = freeze_keys(snap, store_dir=store)
    assert set(result.frozen_keys) == {"A", "B"}
    assert load_frozen(store) == {"A": "1", "B": "2"}


def test_freeze_skips_missing_keys(store):
    snap = _snap({"PRESENT": "yes"})
    result = freeze_keys(snap, keys=["PRESENT", "MISSING"], store_dir=store)
    assert "PRESENT" in result.frozen_keys
    assert "MISSING" in result.skipped_keys


def test_freeze_keys_persists_across_calls(store):
    snap1 = _snap({"A": "1"})
    snap2 = _snap({"B": "2"})
    freeze_keys(snap1, store_dir=store)
    freeze_keys(snap2, store_dir=store)
    frozen = load_frozen(store)
    assert "A" in frozen and "B" in frozen


def test_unfreeze_removes_key(store):
    save_frozen({"X": "val", "Y": "other"}, store)
    removed = unfreeze_keys(["X"], store_dir=store)
    assert removed == ["X"]
    assert "X" not in load_frozen(store)
    assert "Y" in load_frozen(store)


def test_unfreeze_ignores_unknown_keys(store):
    save_frozen({"A": "1"}, store)
    removed = unfreeze_keys(["NOPE"], store_dir=store)
    assert removed == []


def test_check_freeze_no_violations(store):
    save_frozen({"KEY": "correct"}, store)
    snap = _snap({"KEY": "correct"})
    assert check_freeze(snap, store_dir=store) == []


def test_check_freeze_changed_value(store):
    save_frozen({"KEY": "original"}, store)
    snap = _snap({"KEY": "modified"})
    violations = check_freeze(snap, store_dir=store)
    assert len(violations) == 1
    assert violations[0].key == "KEY"
    assert "changed" in violations[0].reason


def test_check_freeze_missing_key(store):
    save_frozen({"GONE": "val"}, store)
    snap = _snap({"OTHER": "val"})
    violations = check_freeze(snap, store_dir=store)
    assert any(v.key == "GONE" for v in violations)


def test_freeze_summary_no_skipped():
    result = FreezeResult(frozen_keys=["A", "B"], skipped_keys=[])
    summary = freeze_summary(result)
    assert "2" in summary
    assert "Skipped" not in summary


def test_freeze_summary_with_skipped():
    result = FreezeResult(frozen_keys=["A"], skipped_keys=["MISSING"])
    summary = freeze_summary(result)
    assert "Skipped" in summary
