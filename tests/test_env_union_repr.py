from envsnap.env_union import UnionResult, UnionConflict


def test_union_result_repr_keys():
    r = UnionResult(env={"A": "1", "B": "2"}, sources={}, conflicts={})
    assert "keys=2" in repr(r)


def test_union_result_repr_conflicts():
    r = UnionResult(
        env={"A": "1"},
        sources={"A": "prod"},
        conflicts={"A": ["prod", "staging"]},
    )
    assert "conflicts=1" in repr(r)


def test_union_conflict_str():
    exc = UnionConflict("SECRET", ["prod", "dev"])
    assert "SECRET" in str(exc)
    assert "prod" in str(exc)
    assert "dev" in str(exc)


def test_union_conflict_attributes():
    exc = UnionConflict("X", ["a", "b"])
    assert exc.key == "X"
    assert exc.labels == ["a", "b"]


def test_union_result_env_is_dict():
    r = UnionResult(env={}, sources={}, conflicts={})
    assert isinstance(r.env, dict)
    assert isinstance(r.sources, dict)
    assert isinstance(r.conflicts, dict)
