import pytest
from envsnap.env_dedup import find_duplicates, dedup_snapshot, dedup_summary, DedupResult


def _snap(**kwargs):
    return dict(kwargs)


def test_find_duplicates_none():
    env = _snap(A="1", B="2", C="3")
    assert find_duplicates(env) == {}


def test_find_duplicates_single_group():
    env = _snap(A="x", B="x", C="y")
    result = find_duplicates(env)
    assert "x" in result
    assert set(result["x"]) == {"A", "B"}


def test_find_duplicates_multiple_groups():
    env = _snap(A="x", B="x", C="y", D="y")
    result = find_duplicates(env)
    assert set(result["x"]) == {"A", "B"}
    assert set(result["y"]) == {"C", "D"}


def test_dedup_keeps_first_by_default():
    env = _snap(B="same", A="same", C="other")
    result = dedup_snapshot(env)
    assert "A" in result.snapshot
    assert "B" not in result.snapshot
    assert "C" in result.snapshot


def test_dedup_keeps_last():
    env = _snap(A="same", B="same", C="other")
    result = dedup_snapshot(env, keep="last")
    assert "B" in result.snapshot
    assert "A" not in result.snapshot


def test_dedup_removed_list():
    env = _snap(A="dup", B="dup", C="unique")
    result = dedup_snapshot(env)
    assert "B" in result.removed
    assert "A" not in result.removed


def test_dedup_no_duplicates_returns_same_keys():
    env = _snap(X="1", Y="2", Z="3")
    result = dedup_snapshot(env)
    assert set(result.snapshot.keys()) == {"X", "Y", "Z"}
    assert result.removed == []


def test_dedup_ignore_empty_true():
    env = _snap(A="", B="", C="val")
    result = dedup_snapshot(env, ignore_empty=True)
    assert "A" in result.snapshot
    assert "B" in result.snapshot
    assert result.removed == []


def test_dedup_ignore_empty_false():
    env = _snap(A="", B="", C="val")
    result = dedup_snapshot(env, ignore_empty=False)
    assert len(result.removed) == 1


def test_dedup_result_repr():
    env = _snap(A="v", B="v")
    result = dedup_snapshot(env)
    r = repr(result)
    assert "DedupResult" in r
    assert "removed=1" in r


def test_dedup_summary_no_duplicates():
    env = _snap(A="1", B="2")
    result = dedup_snapshot(env)
    assert "No duplicate" in dedup_summary(result)


def test_dedup_summary_with_duplicates():
    env = _snap(A="shared", B="shared")
    result = dedup_snapshot(env)
    summary = dedup_summary(result)
    assert "Removed" in summary
    assert "removed" in summary
