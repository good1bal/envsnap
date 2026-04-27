"""Tests for envsnap.env_classify."""
import pytest
from envsnap.env_classify import (
    classify,
    classify_summary,
    ClassifyResult,
    OTHER,
    _DEFAULT_RULES,
)


def _env(**kwargs: str):
    return dict(kwargs)


def test_classify_returns_classify_result():
    result = classify(_env(FOO="bar"))
    assert isinstance(result, ClassifyResult)


def test_classify_secret_key():
    result = classify(_env(DB_PASSWORD="s3cr3t"))
    assert "secrets" in result.categories
    assert "DB_PASSWORD" in result.categories["secrets"]


def test_classify_token_key():
    result = classify(_env(GITHUB_TOKEN="abc"))
    assert result.key_map["GITHUB_TOKEN"] == "secrets"


def test_classify_database_key():
    result = classify(_env(DB_HOST="localhost", DATABASE_URL="postgres://..."))
    # DB_HOST matches 'networking' (HOST) before 'database' (DB_)
    assert result.key_map["DATABASE_URL"] == "database"


def test_classify_networking_key():
    result = classify(_env(APP_PORT="8080"))
    assert result.key_map["APP_PORT"] == "networking"


def test_classify_filesystem_key():
    result = classify(_env(LOG_DIR="/var/log"))
    # LOG matches logging before DIR matches filesystem — first rule wins
    assert result.key_map["LOG_DIR"] == "logging"


def test_classify_other_key():
    result = classify(_env(FEATURE_FLAG="true"))
    assert result.key_map["FEATURE_FLAG"] == OTHER
    assert "FEATURE_FLAG" in result.categories[OTHER]


def test_classify_empty_env():
    result = classify({})
    assert result.categories == {}
    assert result.key_map == {}


def test_classify_custom_rules():
    rules = [("CUSTOM", "custom_cat")]
    result = classify(_env(CUSTOM_KEY="val", OTHER_KEY="val"), rules=rules)
    assert result.key_map["CUSTOM_KEY"] == "custom_cat"
    assert result.key_map["OTHER_KEY"] == OTHER


def test_classify_key_map_covers_all_keys():
    env = _env(SECRET_KEY="x", APP_PORT="80", RANDOM="y")
    result = classify(env)
    assert set(result.key_map.keys()) == set(env.keys())


def test_classify_categories_cover_all_keys():
    env = _env(SECRET_KEY="x", APP_PORT="80", RANDOM="y")
    result = classify(env)
    all_keys = [k for keys in result.categories.values() for k in keys]
    assert sorted(all_keys) == sorted(env.keys())


def test_classify_summary_contains_category_names():
    result = classify(_env(SECRET_KEY="x", APP_PORT="80"))
    summary = classify_summary(result)
    assert "secrets" in summary
    assert "networking" in summary


def test_classify_repr():
    result = classify(_env(SECRET_KEY="x"))
    assert "ClassifyResult" in repr(result)


def test_classify_custom_key_fn():
    # key_fn that lowercases — patterns are uppercased internally so still match
    result = classify(_env(secret_key="x"), key_fn=lambda k: k.upper())
    assert result.key_map["secret_key"] == "secrets"
