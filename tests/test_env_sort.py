"""Tests for envsnap.env_sort."""
import pytest
from envsnap.env_sort import sort_snapshot, sort_keys, group_sorted


@pytest.fixture()
def env():
    return {
        "ZEBRA": "last",
        "APPLE": "first",
        "MANGO": "middle",
        "DB_URL": "postgres",
    }


def test_sort_by_key_ascending(env):
    result = sort_snapshot(env, by="key")
    assert list(result.keys()) == ["APPLE", "DB_URL", "MANGO", "ZEBRA"]


def test_sort_by_key_descending(env):
    result = sort_snapshot(env, by="key", reverse=True)
    assert list(result.keys())[0] == "ZEBRA"


def test_sort_by_value(env):
    result = sort_snapshot(env, by="value")
    assert list(result.keys()) == ["APPLE", "MANGO", "DB_URL", "ZEBRA"]


def test_sort_by_length(env):
    result = sort_snapshot(env, by="length")
    keys = list(result.keys())
    assert keys[0] == "DB_URL"  # length 6
    assert keys[-1] == "MANGO" or keys[-1] == "APPLE" or keys[-1] == "ZEBRA"  # length 5


def test_sort_keys_returns_list(env):
    result = sort_keys(env, by="key")
    assert isinstance(result, list)
    assert result == ["APPLE", "DB_URL", "MANGO", "ZEBRA"]


def test_sort_unknown_key_raises(env):
    with pytest.raises(ValueError, match="Unknown sort key"):
        sort_snapshot(env, by="unknown")  # type: ignore[arg-type]


def test_sort_empty_snapshot():
    assert sort_snapshot({}) == {}


def test_group_sorted_buckets(env):
    groups = group_sorted(env, by="key")
    assert "A" in groups
    assert "APPLE" in groups["A"]
    assert "Z" in groups
    assert "ZEBRA" in groups["Z"]


def test_group_sorted_all_keys_present(env):
    groups = group_sorted(env)
    all_keys = [k for bucket in groups.values() for k in bucket]
    assert set(all_keys) == set(env.keys())
