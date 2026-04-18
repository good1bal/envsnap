"""Tests for envsnap.export module."""

import json
import pytest
from envsnap.export import to_json, to_dotenv, to_csv, from_json


def _snap(vars_: dict | None = None) -> dict:
    return {
        "label": "test",
        "timestamp": "2024-01-01T00:00:00",
        "checksum": "abc123",
        "vars": vars_ or {"APP_ENV": "production", "PORT": "8080"},
    }


class TestToJson:
    def test_returns_valid_json(self):
        result = to_json(_snap())
        parsed = json.loads(result)
        assert parsed["vars"]["PORT"] == "8080"

    def test_keys_are_sorted(self):
        result = to_json(_snap())
        assert result.index('"APP_ENV"') < result.index('"PORT"')

    def test_custom_indent(self):
        result = to_json(_snap(), indent=4)
        assert "    " in result


class TestToDotenv:
    def test_basic_output(self):
        result = to_dotenv(_snap({"KEY": "value"}))
        assert 'KEY="value"' in result

    def test_sorted_keys(self):
        result = to_dotenv(_snap({"Z_KEY": "1", "A_KEY": "2"}))
        assert result.index("A_KEY") < result.index("Z_KEY")

    def test_escapes_double_quotes(self):
        result = to_dotenv(_snap({"MSG": 'say "hi"'}))
        assert 'MSG="say \\"hi\\""' in result

    def test_empty_vars(self):
        result = to_dotenv(_snap({}))
        assert result == ""

    def test_ends_with_newline(self):
        result = to_dotenv(_snap({"A": "1"}))
        assert result.endswith("\n")


class TestToCsv:
    def test_has_header(self):
        result = to_csv(_snap())
        assert result.startswith("key,value\n")

    def test_contains_vars(self):
        result = to_csv(_snap({"FOO": "bar"}))
        assert "FOO,bar" in result


class TestFromJson:
    def test_round_trip(self):
        snap = _snap()
        assert from_json(to_json(snap)) == snap

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="missing 'vars'"):
            from_json(json.dumps({"label": "bad"}))
