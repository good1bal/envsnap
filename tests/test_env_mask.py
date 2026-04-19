"""Tests for envsnap.env_mask."""
import pytest
from envsnap.env_mask import mask_snapshot, mask_summary, MaskResult


def _snap(**kwargs):
    base = {"APP_HOST": "localhost", "APP_PORT": "8080"}
    base.update(kwargs)
    return base


def test_mask_auto_detects_secret():
    snap = _snap(APP_SECRET="abc123")
    result = mask_snapshot(snap)
    assert result.masked["APP_SECRET"] == "***"


def test_mask_auto_detects_password():
    snap = _snap(DB_PASSWORD="hunter2")
    result = mask_snapshot(snap)
    assert result.masked["DB_PASSWORD"] == "***"


def test_mask_preserves_non_sensitive():
    snap = _snap(APP_SECRET="s")
    result = mask_snapshot(snap)
    assert result.masked["APP_HOST"] == "localhost"
    assert result.masked["APP_PORT"] == "8080"


def test_mask_explicit_keys():
    snap = _snap(MY_CUSTOM="value")
    result = mask_snapshot(snap, keys=["MY_CUSTOM"], auto_detect=False)
    assert result.masked["MY_CUSTOM"] == "***"


def test_mask_explicit_keys_ignores_auto_when_disabled():
    snap = _snap(APP_TOKEN="tok")
    result = mask_snapshot(snap, keys=[], auto_detect=False)
    assert result.masked["APP_TOKEN"] == "tok"
    assert result.mask_keys == []


def test_mask_custom_placeholder():
    snap = _snap(APP_SECRET="s")
    result = mask_snapshot(snap, placeholder="[REDACTED]")
    assert result.masked["APP_SECRET"] == "[REDACTED]"


def test_mask_result_repr():
    snap = _snap(APP_SECRET="s")
    result = mask_snapshot(snap)
    assert "MaskResult" in repr(result)


def test_mask_keys_sorted():
    snap = {"Z_TOKEN": "a", "A_SECRET": "b", "PLAIN": "c"}
    result = mask_snapshot(snap)
    assert result.mask_keys == sorted(result.mask_keys)


def test_mask_summary_no_keys():
    snap = _snap()
    result = mask_snapshot(snap)
    assert mask_summary(result) == "No keys masked."


def test_mask_summary_with_keys():
    snap = _snap(APP_SECRET="s")
    result = mask_snapshot(snap)
    summary = mask_summary(result)
    assert "APP_SECRET" in summary
    assert "Masked 1 key(s)" in summary


def test_mask_missing_explicit_key_ignored():
    snap = _snap()
    result = mask_snapshot(snap, keys=["NONEXISTENT"], auto_detect=False)
    assert result.mask_keys == []
