"""Tests for RollbackResult repr and attribute contract."""
from __future__ import annotations

from envsnap.env_rollback import RollbackResult, rollback


def _snap(label: str, env: dict) -> dict:
    return {"label": label, "env": env, "meta": {}}


def test_rollback_result_has_expected_fields():
    current = _snap("new", {"X": "2"})
    target = _snap("old", {"X": "1"})
    result = rollback(current, target)
    assert hasattr(result, "original")
    assert hasattr(result, "reverted")
    assert hasattr(result, "diff")
    assert hasattr(result, "keys_restored")
    assert hasattr(result, "keys_removed")
    assert hasattr(result, "keys_unchanged")


def test_rollback_result_original_is_dict():
    current = _snap("new", {"X": "2"})
    target = _snap("old", {"X": "1"})
    result = rollback(current, target)
    assert isinstance(result.original, dict)


def test_rollback_result_reverted_is_dict():
    current = _snap("new", {"X": "2"})
    target = _snap("old", {"X": "1"})
    result = rollback(current, target)
    assert isinstance(result.reverted, dict)


def test_rollback_result_lists_are_lists():
    current = _snap("new", {"A": "2", "B": "same"})
    target = _snap("old", {"A": "1", "B": "same"})
    result = rollback(current, target)
    assert isinstance(result.keys_restored, list)
    assert isinstance(result.keys_removed, list)
    assert isinstance(result.keys_unchanged, list)


def test_rollback_result_counts_sum_to_total_keys():
    current = _snap("new", {"A": "2", "B": "same", "C": "extra"})
    target = _snap("old", {"A": "1", "B": "same"})
    result = rollback(current, target)
    total = len(result.keys_restored) + len(result.keys_removed) + len(result.keys_unchanged)
    all_keys = set(current["env"]) | set(target["env"])
    assert total == len(all_keys)
