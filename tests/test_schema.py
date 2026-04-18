"""Tests for envsnap.schema."""
import json
import pytest
from pathlib import Path
from envsnap.schema import load_schema, save_schema, schema_from_snapshot


def test_save_and_load_roundtrip(tmp_path):
    p = tmp_path / "schema.json"
    save_schema(p, required=["FOO", "BAR"], forbidden=["SECRET"])
    schema = load_schema(p)
    assert schema["required"] == ["FOO", "BAR"]
    assert schema["forbidden"] == ["SECRET"]


def test_load_schema_only_known_keys(tmp_path):
    p = tmp_path / "schema.json"
    p.write_text(json.dumps({"required": ["A"], "unknown_field": True}))
    schema = load_schema(p)
    assert "unknown_field" not in schema
    assert "required" in schema


def test_save_schema_omits_empty_fields(tmp_path):
    p = tmp_path / "schema.json"
    save_schema(p, required=["X"])
    data = json.loads(p.read_text())
    assert "forbidden" not in data
    assert "patterns" not in data


def test_save_schema_with_patterns(tmp_path):
    p = tmp_path / "schema.json"
    save_schema(p, patterns={"PORT": r"\d+"})
    schema = load_schema(p)
    assert schema["patterns"]["PORT"] == r"\d+"


def test_schema_from_snapshot():
    snap = {"label": "prod", "env": {"FOO": "1", "BAR": "2"}, "meta": {}}
    schema = schema_from_snapshot(snap)
    assert set(schema["required"]) == {"FOO", "BAR"}


def test_schema_from_empty_snapshot():
    snap = {"label": "empty", "env": {}, "meta": {}}
    schema = schema_from_snapshot(snap)
    assert schema["required"] == []
