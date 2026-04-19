import pytest
from envsnap.env_extract import extract_keys, extract_summary, ExtractResult


def _snap():
    return {"APP_HOST": "localhost", "APP_PORT": "8080", "DB_URL": "postgres://"}


def test_extract_keys_basic():
    result = extract_keys(_snap(), ["APP_HOST", "APP_PORT"])
    assert result.env == {"APP_HOST": "localhost", "APP_PORT": "8080"}


def test_extract_keys_extracted_list():
    result = extract_keys(_snap(), ["APP_HOST"])
    assert "APP_HOST" in result.extracted
    assert len(result.extracted) == 1


def test_extract_keys_missing_skipped_by_default():
    result = extract_keys(_snap(), ["APP_HOST", "MISSING_KEY"])
    assert "MISSING_KEY" not in result.env
    assert "MISSING_KEY" in result.missing


def test_extract_keys_missing_filled_with_default():
    result = extract_keys(_snap(), ["MISSING_KEY"], skip_missing=False, default="fallback")
    assert result.env["MISSING_KEY"] == "fallback"


def test_extract_keys_missing_filled_with_empty_string():
    result = extract_keys(_snap(), ["MISSING_KEY"], skip_missing=False)
    assert result.env["MISSING_KEY"] == ""


def test_extract_keys_all_missing():
    result = extract_keys(_snap(), ["X", "Y"])
    assert result.env == {}
    assert result.missing == ["X", "Y"]


def test_extract_keys_empty_key_list():
    result = extract_keys(_snap(), [])
    assert result.env == {}
    assert result.extracted == []
    assert result.missing == []


def test_extract_does_not_mutate_original():
    snap = _snap()
    extract_keys(snap, ["APP_HOST"])
    assert len(snap) == 3


def test_extract_result_repr():
    result = ExtractResult(env={}, extracted=["A"], missing=["B"])
    r = repr(result)
    assert "extracted=1" in r
    assert "missing=1" in r


def test_extract_summary_no_missing():
    result = extract_keys(_snap(), ["APP_HOST"])
    summary = extract_summary(result)
    assert "1 key" in summary
    assert "Missing" not in summary


def test_extract_summary_with_missing():
    result = extract_keys(_snap(), ["APP_HOST", "GHOST"])
    summary = extract_summary(result)
    assert "Missing" in summary
    assert "GHOST" in summary
