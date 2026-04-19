"""Tests for envsnap.env_cast."""

import pytest

from envsnap.env_cast import (
    CastError,
    cast,
    cast_bool,
    cast_float,
    cast_int,
    cast_list,
    cast_snapshot,
)


# --- cast_bool ---

@pytest.mark.parametrize("v", ["1", "true", "True", "TRUE", "yes", "on"])
def test_cast_bool_true(v):
    assert cast_bool(v) is True


@pytest.mark.parametrize("v", ["0", "false", "False", "no", "off"])
def test_cast_bool_false(v):
    assert cast_bool(v) is False


def test_cast_bool_invalid():
    with pytest.raises(CastError):
        cast_bool("maybe")


# --- cast_int ---

def test_cast_int_valid():
    assert cast_int("42") == 42


def test_cast_int_negative():
    assert cast_int("-7") == -7


def test_cast_int_invalid():
    with pytest.raises(CastError):
        cast_int("three")


# --- cast_float ---

def test_cast_float_valid():
    assert cast_float("3.14") == pytest.approx(3.14)


def test_cast_float_invalid():
    with pytest.raises(CastError):
        cast_float("pi")


# --- cast_list ---

def test_cast_list_basic():
    assert cast_list("a,b,c") == ["a", "b", "c"]


def test_cast_list_custom_sep():
    assert cast_list("x:y:z", sep=":") == ["x", "y", "z"]


def test_cast_list_strips_whitespace():
    assert cast_list(" a , b , c ") == ["a", "b", "c"]


# --- cast (dispatch) ---

def test_cast_unknown_type():
    with pytest.raises(CastError, match="Unknown type"):
        cast("value", "datetime")


def test_cast_str_passthrough():
    assert cast("hello", "str") == "hello"


# --- cast_snapshot ---

def test_cast_snapshot_applies_schema():
    env = {"PORT": "8080", "DEBUG": "true", "RATIO": "0.5", "NAME": "app"}
    schema = {"PORT": "int", "DEBUG": "bool", "RATIO": "float"}
    result = cast_snapshot(env, schema)
    assert result["PORT"] == 8080
    assert result["DEBUG"] is True
    assert result["RATIO"] == pytest.approx(0.5)
    assert result["NAME"] == "app"  # no schema entry → str


def test_cast_snapshot_empty_schema():
    env = {"A": "1", "B": "2"}
    result = cast_snapshot(env, {})
    assert result == {"A": "1", "B": "2"}
