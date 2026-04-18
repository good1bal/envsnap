"""Tests for envsnap.snapshot module."""

import json
import os
import tempfile

import pytest

from envsnap.snapshot import capture, load, save, _checksum


def test_capture_returns_required_keys():
    snap = capture(label="test")
    assert "label" in snap
    assert "timestamp" in snap
    assert "env" in snap
    assert "checksum" in snap


def test_capture_label_default():
    snap = capture()
    assert snap["label"] == "snapshot"


def test_capture_excludes_prefixes(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "s3cr3t")
    monkeypatch.setenv("PUBLIC_KEY", "pub")
    snap = capture(exclude_prefixes=("SECRET_",))
    assert "SECRET_KEY" not in snap["env"]
    assert "PUBLIC_KEY" in snap["env"]


def test_checksum_is_stable():
    env = {"FOO": "bar", "BAZ": "qux"}
    assert _checksum(env) == _checksum(env)


def test_checksum_changes_with_value():
    env1 = {"FOO": "bar"}
    env2 = {"FOO": "baz"}
    assert _checksum(env1) != _checksum(env2)


def test_save_and_load_roundtrip():
    snap = capture(label="roundtrip")
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        path = tmp.name
    try:
        save(snap, path)
        loaded = load(path)
        assert loaded["label"] == "roundtrip"
        assert loaded["env"] == snap["env"]
    finally:
        os.unlink(path)
