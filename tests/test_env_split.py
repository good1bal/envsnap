import pytest
from envsnap.env_split import split_by_prefix, split_by_keys, split_summary, SplitResult


def _env():
    return {
        "APP_HOST": "localhost",
        "APP_PORT": "8080",
        "DB_HOST": "db.local",
        "DB_PORT": "5432",
        "SECRET_KEY": "abc123",
    }


def test_split_by_prefix_basic():
    result = split_by_prefix(_env(), ["APP_", "DB_"])
    assert set(result.parts["APP_"].keys()) == {"APP_HOST", "APP_PORT"}
    assert set(result.parts["DB_"].keys()) == {"DB_HOST", "DB_PORT"}


def test_split_by_prefix_remainder():
    result = split_by_prefix(_env(), ["APP_", "DB_"])
    assert result.remainder == {"SECRET_KEY": "abc123"}


def test_split_by_prefix_strip_prefix():
    result = split_by_prefix(_env(), ["APP_"], strip_prefix=True)
    assert "HOST" in result.parts["APP_"]
    assert "PORT" in result.parts["APP_"]


def test_split_by_prefix_no_match_returns_empty_bucket():
    result = split_by_prefix(_env(), ["MISSING_"])
    assert result.parts["MISSING_"] == {}
    assert len(result.remainder) == len(_env())


def test_split_by_prefix_label():
    result = split_by_prefix(_env(), ["APP_"], label="prod")
    assert result.source_label == "prod"


def test_split_by_keys_basic():
    groups = {"web": ["APP_HOST", "APP_PORT"], "db": ["DB_HOST", "DB_PORT"]}
    result = split_by_keys(_env(), groups)
    assert result.parts["web"] == {"APP_HOST": "localhost", "APP_PORT": "8080"}
    assert result.parts["db"] == {"DB_HOST": "db.local", "DB_PORT": "5432"}


def test_split_by_keys_missing_key_skipped():
    groups = {"web": ["APP_HOST", "NONEXISTENT"]}
    result = split_by_keys(_env(), groups)
    assert "NONEXISTENT" not in result.parts["web"]
    assert "APP_HOST" in result.parts["web"]


def test_split_by_keys_remainder():
    groups = {"web": ["APP_HOST", "APP_PORT"]}
    result = split_by_keys(_env(), groups)
    assert "SECRET_KEY" in result.remainder
    assert "DB_HOST" in result.remainder


def test_split_summary_output():
    result = split_by_prefix(_env(), ["APP_", "DB_"], label="staging")
    s = split_summary(result)
    assert "staging" in s
    assert "APP_" in s
    assert "DB_" in s
    assert "remainder" in s


def test_split_result_repr():
    result = split_by_prefix(_env(), ["APP_"])
    r = repr(result)
    assert "SplitResult" in r
    assert "APP_" in r
