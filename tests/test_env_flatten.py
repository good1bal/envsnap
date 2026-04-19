import pytest
from envsnap.env_flatten import flatten, unflatten, flatten_summary, FlattenError


def test_flatten_simple_dict():
    data = {"A": "1", "B": "2"}
    assert flatten(data) == {"A": "1", "B": "2"}


def test_flatten_nested_dict():
    data = {"DB": {"HOST": "localhost", "PORT": "5432"}}
    result = flatten(data)
    assert result == {"DB__HOST": "localhost", "DB__PORT": "5432"}


def test_flatten_deeply_nested():
    data = {"A": {"B": {"C": "deep"}}}
    assert flatten(data) == {"A__B__C": "deep"}


def test_flatten_custom_separator():
    data = {"APP": {"ENV": "prod"}}
    assert flatten(data, separator=".") == {"APP.ENV": "prod"}


def test_flatten_list_values():
    data = {"HOSTS": ["a", "b"]}
    result = flatten(data)
    assert result == {"HOSTS__0": "a", "HOSTS__1": "b"}


def test_flatten_none_value_becomes_empty_string():
    data = {"KEY": None}
    assert flatten(data) == {"KEY": ""}


def test_flatten_int_value_becomes_string():
    data = {"PORT": 8080}
    assert flatten(data) == {"PORT": "8080"}


def test_flatten_empty_dict():
    assert flatten({}) == {}


def test_unflatten_simple():
    data = {"A": "1", "B": "2"}
    assert unflatten(data) == {"A": "1", "B": "2"}


def test_unflatten_nested():
    data = {"DB__HOST": "localhost", "DB__PORT": "5432"}
    result = unflatten(data)
    assert result == {"DB": {"HOST": "localhost", "PORT": "5432"}}


def test_unflatten_deeply_nested():
    data = {"A__B__C": "deep"}
    assert unflatten(data) == {"A": {"B": {"C": "deep"}}}


def test_unflatten_custom_separator():
    data = {"APP.ENV": "prod"}
    assert unflatten(data, separator=".") == {"APP": {"ENV": "prod"}}


def test_flatten_summary_message():
    original = {"A": {"X": "1"}, "B": "2"}
    flat = flatten(original)
    msg = flatten_summary(original, flat)
    assert "2 top-level" in msg
    assert "2 flat" in msg
