"""Tests for envsnap.env_count."""
import pytest
from envsnap.env_count import CountResult, count_keys, count_summary


def _env(**kwargs: str):
    return dict(kwargs)


# ---------------------------------------------------------------------------
# count_keys
# ---------------------------------------------------------------------------

def test_count_keys_total():
    env = _env(FOO="1", BAR="2", BAZ="3")
    result = count_keys(env)
    assert result.total == 3


def test_count_keys_empty_env():
    result = count_keys({})
    assert result.total == 0
    assert result.empty_values == 0
    assert result.non_empty_values == 0


def test_count_keys_empty_values():
    env = _env(FOO="", BAR="hello", BAZ="")
    result = count_keys(env)
    assert result.empty_values == 2
    assert result.non_empty_values == 1


def test_count_keys_all_non_empty():
    env = _env(A="1", B="2")
    result = count_keys(env)
    assert result.empty_values == 0
    assert result.non_empty_values == 2


def test_count_keys_sensitive_detection():
    env = _env(DB_PASSWORD="secret", API_TOKEN="tok", HOST="localhost")
    result = count_keys(env)
    assert result.sensitive_count == 2


def test_count_keys_no_sensitive():
    env = _env(HOST="localhost", PORT="5432")
    result = count_keys(env)
    assert result.sensitive_count == 0


def test_count_keys_by_prefix_single():
    env = _env(AWS_REGION="us-east-1", AWS_KEY="k", GCP_PROJECT="p")
    result = count_keys(env, prefixes=["AWS"])
    assert result.by_prefix["AWS"] == 2


def test_count_keys_by_prefix_multiple():
    env = _env(AWS_REGION="us-east-1", AWS_KEY="k", GCP_PROJECT="p", GCP_ZONE="z")
    result = count_keys(env, prefixes=["AWS", "GCP"])
    assert result.by_prefix["AWS"] == 2
    assert result.by_prefix["GCP"] == 2


def test_count_keys_by_prefix_no_match():
    env = _env(FOO="1", BAR="2")
    result = count_keys(env, prefixes=["MISSING"])
    assert result.by_prefix["MISSING"] == 0


def test_count_keys_no_prefixes_returns_empty_dict():
    env = _env(FOO="1")
    result = count_keys(env)
    assert result.by_prefix == {}


# ---------------------------------------------------------------------------
# count_summary
# ---------------------------------------------------------------------------

def test_count_summary_contains_total():
    result = CountResult(total=5, empty_values=1, non_empty_values=4, sensitive_count=2)
    summary = count_summary(result)
    assert "5" in summary
    assert "Total keys" in summary


def test_count_summary_contains_sensitive():
    result = CountResult(total=3, empty_values=0, non_empty_values=3, sensitive_count=1)
    summary = count_summary(result)
    assert "Sensitive" in summary
    assert "1" in summary


def test_count_summary_with_prefix_breakdown():
    result = CountResult(
        total=4,
        by_prefix={"AWS": 3, "GCP": 1},
        empty_values=0,
        non_empty_values=4,
        sensitive_count=0,
    )
    summary = count_summary(result)
    assert "AWS: 3" in summary
    assert "GCP: 1" in summary


def test_count_summary_no_prefix_section_when_empty():
    result = CountResult(total=2, empty_values=0, non_empty_values=2, sensitive_count=0)
    summary = count_summary(result)
    assert "By prefix" not in summary
