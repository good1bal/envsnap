"""Tests for envsnap.pin module."""
import pytest

from envsnap.pin import check_pins, load_pins, pin_key, save_pins, unpin_key


def test_load_pins_missing_file_returns_empty(tmp_path):
    assert load_pins(str(tmp_path)) == {}


def test_pin_key_creates_entry(tmp_path):
    pins = pin_key("APP_ENV", "production", str(tmp_path))
    assert pins["APP_ENV"] == "production"


def test_pin_key_persists(tmp_path):
    pin_key("APP_ENV", "production", str(tmp_path))
    loaded = load_pins(str(tmp_path))
    assert loaded["APP_ENV"] == "production"


def test_pin_key_multiple(tmp_path):
    pin_key("A", "1", str(tmp_path))
    pin_key("B", "2", str(tmp_path))
    pins = load_pins(str(tmp_path))
    assert pins == {"A": "1", "B": "2"}


def test_unpin_key_removes_entry(tmp_path):
    pin_key("APP_ENV", "production", str(tmp_path))
    unpin_key("APP_ENV", str(tmp_path))
    assert "APP_ENV" not in load_pins(str(tmp_path))


def test_unpin_missing_key_no_error(tmp_path):
    unpin_key("NONEXISTENT", str(tmp_path))  # should not raise


def test_check_pins_all_match(tmp_path):
    pin_key("APP_ENV", "prod", str(tmp_path))
    violations = check_pins({"APP_ENV": "prod"}, str(tmp_path))
    assert violations == []


def test_check_pins_value_mismatch(tmp_path):
    pin_key("APP_ENV", "prod", str(tmp_path))
    violations = check_pins({"APP_ENV": "staging"}, str(tmp_path))
    assert len(violations) == 1
    assert "APP_ENV" in violations[0]


def test_check_pins_key_missing(tmp_path):
    pin_key("REQUIRED", "yes", str(tmp_path))
    violations = check_pins({}, str(tmp_path))
    assert any("not present" in v for v in violations)


def test_check_pins_no_pins_no_violations(tmp_path):
    violations = check_pins({"ANY": "value"}, str(tmp_path))
    assert violations == []


def test_save_and_load_roundtrip(tmp_path):
    data = {"X": "1", "Y": "2"}
    save_pins(data, str(tmp_path))
    assert load_pins(str(tmp_path)) == data
