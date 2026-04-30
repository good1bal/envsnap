"""Tests for envsnap.env_protect."""
from __future__ import annotations

import pytest

from envsnap.env_protect import (
    ProtectResult,
    ProtectViolation,
    check_protected,
    load_protected,
    protect_keys,
    protect_summary,
    save_protected,
)


def _snap(**kwargs) -> dict:
    return {"APP_NAME": "myapp", "DB_HOST": "localhost", **kwargs}


# ---------------------------------------------------------------------------
# load / save round-trip
# ---------------------------------------------------------------------------

def test_load_protected_missing_file_returns_empty(tmp_path):
    assert load_protected(tmp_path) == []


def test_save_and_load_roundtrip(tmp_path):
    save_protected(["DB_HOST", "APP_NAME"], tmp_path)
    result = load_protected(tmp_path)
    assert set(result) == {"DB_HOST", "APP_NAME"}


def test_save_deduplicates(tmp_path):
    save_protected(["KEY", "KEY", "OTHER"], tmp_path)
    assert load_protected(tmp_path).count("KEY") == 1


# ---------------------------------------------------------------------------
# protect_keys
# ---------------------------------------------------------------------------

def test_protect_keys_registers_existing_keys(tmp_path):
    env = _snap()
    result = protect_keys(env, ["DB_HOST"], tmp_path)
    assert "DB_HOST" in result.protected


def test_protect_keys_skips_keys_not_in_env(tmp_path):
    env = _snap()
    result = protect_keys(env, ["MISSING_KEY"], tmp_path)
    assert "MISSING_KEY" not in result.protected


def test_protect_keys_persists_to_store(tmp_path):
    protect_keys(_snap(), ["APP_NAME"], tmp_path)
    assert "APP_NAME" in load_protected(tmp_path)


def test_protect_keys_accumulates_across_calls(tmp_path):
    protect_keys(_snap(), ["APP_NAME"], tmp_path)
    protect_keys(_snap(), ["DB_HOST"], tmp_path)
    stored = load_protected(tmp_path)
    assert "APP_NAME" in stored
    assert "DB_HOST" in stored


def test_protect_keys_env_unchanged(tmp_path):
    env = _snap()
    result = protect_keys(env, ["APP_NAME"], tmp_path)
    assert result.env == env


# ---------------------------------------------------------------------------
# check_protected
# ---------------------------------------------------------------------------

def test_check_protected_no_violations_when_unchanged(tmp_path):
    env = _snap()
    save_protected(["DB_HOST"], tmp_path)
    result = check_protected(env, dict(env), tmp_path)
    assert result.violations == []


def test_check_protected_detects_modified_value(tmp_path):
    original = _snap()
    updated = _snap(DB_HOST="changed.host")
    save_protected(["DB_HOST"], tmp_path)
    result = check_protected(original, updated, tmp_path)
    assert len(result.violations) == 1
    assert result.violations[0].key == "DB_HOST"
    assert result.violations[0].reason == "modified"


def test_check_protected_detects_deleted_key(tmp_path):
    original = _snap()
    updated = {k: v for k, v in _snap().items() if k != "DB_HOST"}
    save_protected(["DB_HOST"], tmp_path)
    result = check_protected(original, updated, tmp_path)
    assert any(v.reason == "deleted" for v in result.violations)


def test_check_protected_ignores_added_keys(tmp_path):
    original = _snap()
    updated = _snap(NEW_KEY="hello")
    save_protected(["DB_HOST"], tmp_path)
    result = check_protected(original, updated, tmp_path)
    assert result.violations == []


def test_check_protected_empty_store_no_violations(tmp_path):
    env = _snap()
    result = check_protected(env, {"DB_HOST": "new"}, tmp_path)
    assert result.violations == []


# ---------------------------------------------------------------------------
# protect_summary
# ---------------------------------------------------------------------------

def test_protect_summary_no_violations(tmp_path):
    env = _snap()
    save_protected(["APP_NAME"], tmp_path)
    result = check_protected(env, dict(env), tmp_path)
    summary = protect_summary(result)
    assert "Violations     : 0" in summary


def test_protect_summary_shows_violation(tmp_path):
    original = _snap()
    updated = _snap(DB_HOST="other")
    save_protected(["DB_HOST"], tmp_path)
    result = check_protected(original, updated, tmp_path)
    summary = protect_summary(result)
    assert "modified" in summary
    assert "DB_HOST" in summary
