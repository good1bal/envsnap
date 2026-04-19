import pytest
from envsnap.env_union import union, union_summary, UnionConflict


def _snap(label, **kwargs):
    return {"label": label, "env": dict(kwargs)}


def test_union_single_snapshot():
    result = union([_snap("a", FOO="1", BAR="2")])
    assert result.env == {"FOO": "1", "BAR": "2"}


def test_union_disjoint_snapshots():
    result = union([_snap("a", FOO="1"), _snap("b", BAR="2")])
    assert result.env == {"FOO": "1", "BAR": "2"}
    assert len(result.conflicts) == 0


def test_union_first_strategy_keeps_first():
    result = union([_snap("a", FOO="1"), _snap("b", FOO="2")], strategy="first")
    assert result.env["FOO"] == "1"
    assert "FOO" in result.conflicts


def test_union_last_strategy_keeps_last():
    result = union([_snap("a", FOO="1"), _snap("b", FOO="2")], strategy="last")
    assert result.env["FOO"] == "2"
    assert "FOO" in result.conflicts


def test_union_error_strategy_raises_on_conflict():
    with pytest.raises(UnionConflict) as exc_info:
        union([_snap("a", FOO="1"), _snap("b", FOO="2")], strategy="error")
    assert exc_info.value.key == "FOO"


def test_union_no_conflict_when_values_agree():
    result = union([_snap("a", FOO="1"), _snap("b", FOO="1")])
    assert result.env["FOO"] == "1"
    assert len(result.conflicts) == 0


def test_union_sources_tracks_origin():
    result = union([_snap("prod", FOO="1"), _snap("staging", BAR="2")])
    assert result.sources["FOO"] == "prod"
    assert result.sources["BAR"] == "staging"


def test_union_empty_list_returns_empty():
    result = union([])
    assert result.env == {}
    assert result.conflicts == {}


def test_union_summary_no_conflicts():
    result = union([_snap("a", X="1")])
    summary = union_summary(result)
    assert "Total keys" in summary
    assert "Conflicts  : 0" in summary


def test_union_summary_with_conflict():
    result = union([_snap("a", X="1"), _snap("b", X="2")])
    summary = union_summary(result)
    assert "Conflicts  : 1" in summary
    assert "X" in summary


def test_repr_contains_key_count():
    result = union([_snap("a", A="1", B="2")])
    assert "keys=2" in repr(result)
