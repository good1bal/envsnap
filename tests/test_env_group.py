import pytest
from envsnap.env_group import group_by_prefix, group_by_mapping, group_summary, EnvGroup


def _snap(vars_: dict, label: str = "test") -> dict:
    return {"label": label, "vars": vars_}


SAMPLE = _snap({
    "AWS_ACCESS_KEY": "abc",
    "AWS_SECRET_KEY": "xyz",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_ENV": "prod",
    "UNRELATED": "val",
})


def test_group_by_prefix_basic():
    groups = group_by_prefix(SAMPLE, ["AWS_", "DB_"])
    assert set(groups["AWS_"].keys) == {"AWS_ACCESS_KEY", "AWS_SECRET_KEY"}
    assert set(groups["DB_"].keys) == {"DB_HOST", "DB_PORT"}


def test_group_by_prefix_other_bucket():
    groups = group_by_prefix(SAMPLE, ["AWS_", "DB_"])
    assert "other" in groups
    assert set(groups["other"].keys) == {"APP_ENV", "UNRELATED"}


def test_group_by_prefix_no_prefixes_returns_all_in_other():
    groups = group_by_prefix(SAMPLE, [])
    assert "other" in groups
    assert len(groups["other"]) == 6


def test_group_by_prefix_custom_other_label():
    groups = group_by_prefix(SAMPLE, ["AWS_"], other_label="misc")
    assert "misc" in groups
    assert "other" not in groups


def test_group_by_prefix_no_overlap():
    groups = group_by_prefix(SAMPLE, ["AWS_", "DB_"])
    all_keys = [k for g in groups.values() for k in g.keys]
    assert len(all_keys) == len(set(all_keys))


def test_group_by_mapping_basic():
    mapping = {"cloud": ["AWS_ACCESS_KEY", "AWS_SECRET_KEY"], "db": ["DB_HOST", "DB_PORT"]}
    groups = group_by_mapping(SAMPLE, mapping)
    assert set(groups["cloud"].keys) == {"AWS_ACCESS_KEY", "AWS_SECRET_KEY"}
    assert set(groups["db"].keys) == {"DB_HOST", "DB_PORT"}


def test_group_by_mapping_ignores_missing_keys():
    mapping = {"cloud": ["AWS_ACCESS_KEY", "NONEXISTENT"]}
    groups = group_by_mapping(SAMPLE, mapping)
    assert "NONEXISTENT" not in groups["cloud"].keys


def test_group_by_mapping_other_bucket():
    mapping = {"cloud": ["AWS_ACCESS_KEY", "AWS_SECRET_KEY"]}
    groups = group_by_mapping(SAMPLE, mapping)
    assert "other" in groups
    assert "DB_HOST" in groups["other"].keys


def test_group_summary_contains_group_names():
    groups = group_by_prefix(SAMPLE, ["AWS_", "DB_"])
    summary = group_summary(groups)
    assert "[AWS_]" in summary
    assert "[DB_]" in summary


def test_group_summary_contains_keys():
    groups = group_by_prefix(SAMPLE, ["AWS_"])
    summary = group_summary(groups)
    assert "AWS_ACCESS_KEY" in summary
    assert "AWS_SECRET_KEY" in summary


def test_env_group_len():
    g = EnvGroup(name="test", keys=["A", "B", "C"])
    assert len(g) == 3
