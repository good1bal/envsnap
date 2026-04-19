import pytest
from envsnap.env_lock import (
    LockViolation,
    lock_keys,
    check_lock,
    lock_summary,
    load_lock,
    save_lock,
)
import json


def _snap(env: dict) -> dict:
    return {"label": "test", "env": env}


def test_lock_keys_extracts_requested(tmp_path):
    snap = _snap({"A": "1", "B": "2", "C": "3"})
    result = lock_keys(snap, ["A", "C"])
    assert result == {"A": "1", "C": "3"}


def test_lock_keys_skips_missing():
    snap = _snap({"A": "1"})
    result = lock_keys(snap, ["A", "MISSING"])
    assert "MISSING" not in result


def test_check_lock_no_violations():
    snap = _snap({"A": "1", "B": "2"})
    locked = {"A": "1", "B": "2"}
    assert check_lock(snap, locked) == []


def test_check_lock_changed_value():
    snap = _snap({"A": "new"})
    locked = {"A": "old"}
    violations = check_lock(snap, locked)
    assert len(violations) == 1
    assert violations[0].key == "A"
    assert violations[0].expected == "old"
    assert violations[0].actual == "new"


def test_check_lock_missing_key():
    snap = _snap({})
    locked = {"A": "1"}
    violations = check_lock(snap, locked)
    assert violations[0].actual is None


def test_lock_violation_str_changed():
    v = LockViolation(key="X", expected="a", actual="b")
    assert "expected 'a'" in str(v)
    assert "got 'b'" in str(v)


def test_lock_violation_str_missing():
    v = LockViolation(key="X", expected="a", actual=None)
    assert "missing" in str(v)


def test_lock_summary_no_violations():
    assert lock_summary([]) == "All locked keys match."


def test_lock_summary_with_violations():
    v = LockViolation(key="A", expected="1", actual="2")
    summary = lock_summary([v])
    assert "Lock violations" in summary
    assert "A" in summary


def test_save_and_load_roundtrip(tmp_path):
    path = str(tmp_path / "lock.json")
    data = {"KEY": "value", "OTHER": "val2"}
    save_lock(data, path)
    loaded = load_lock(path)
    assert loaded == data


def test_load_lock_missing_file_returns_empty(tmp_path):
    path = str(tmp_path / "nonexistent.json")
    assert load_lock(path) == {}
