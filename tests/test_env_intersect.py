import pytest
from envsnap.env_intersect import intersect, intersect_summary, IntersectResult


def _snap(**kwargs):
    return dict(kwargs)


def test_intersect_empty_list():
    result = intersect([])
    assert result.common == {}
    assert result.agreed == {}
    assert result.conflicted == {}


def test_intersect_single_snapshot():
    snap = _snap(A="1", B="2")
    result = intersect([snap])
    assert result.agreed == {"A": "1", "B": "2"}
    assert result.conflicted == {}


def test_intersect_disjoint_snapshots():
    a = _snap(A="1")
    b = _snap(B="2")
    result = intersect([a, b])
    assert result.common == {}


def test_intersect_common_keys_all_agree():
    a = _snap(X="hello", Y="world")
    b = _snap(X="hello", Z="other")
    result = intersect([a, b])
    assert "X" in result.agreed
    assert result.agreed["X"] == "hello"
    assert "Y" not in result.common
    assert "Z" not in result.common


def test_intersect_conflicted_values():
    a = _snap(KEY="val1")
    b = _snap(KEY="val2")
    result = intersect([a, b])
    assert "KEY" in result.conflicted
    assert set(result.conflicted["KEY"]) == {"val1", "val2"}
    assert "KEY" not in result.agreed


def test_intersect_three_snapshots_partial_conflict():
    a = _snap(A="1", B="same")
    b = _snap(A="2", B="same")
    c = _snap(A="1", B="same")
    result = intersect([a, b, c])
    assert "A" in result.conflicted
    assert "B" in result.agreed


def test_intersect_summary_no_conflicts():
    a = _snap(FOO="bar")
    b = _snap(FOO="bar")
    result = intersect([a, b])
    summary = intersect_summary(result)
    assert "Agreed" in summary
    assert "1" in summary


def test_intersect_summary_with_conflicts():
    a = _snap(K="v1")
    b = _snap(K="v2")
    result = intersect([a, b])
    summary = intersect_summary(result)
    assert "K" in summary
    assert "v1" in summary
    assert "v2" in summary


def test_repr():
    result = IntersectResult(common={"A": "1"}, agreed={"A": "1"}, conflicted={})
    assert "IntersectResult" in repr(result)
    assert "agreed=1" in repr(result)
