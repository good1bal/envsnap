"""Tests for envsnap.env_version."""
from __future__ import annotations

import json
import pytest

from envsnap.env_version import (
    VersionEntry,
    VersionStore,
    add_version,
    load_versions,
    save_versions,
    version_summary,
)


def _env(extra: dict | None = None) -> dict:
    base = {"APP_ENV": "production", "LOG_LEVEL": "info"}
    if extra:
        base.update(extra)
    return base


def test_load_versions_missing_file_returns_empty(tmp_path):
    store = load_versions(str(tmp_path / "versions.json"))
    assert len(store) == 0
    assert store.latest() is None


def test_add_version_increments(tmp_path):
    store = VersionStore()
    e1 = add_version(store, label="v1", env=_env())
    e2 = add_version(store, label="v2", env=_env({"NEW": "1"}))
    assert e1.version == 1
    assert e2.version == 2


def test_add_version_stores_env(tmp_path):
    store = VersionStore()
    env = _env()
    entry = add_version(store, label="test", env=env)
    assert entry.env == env


def test_add_version_checksum_changes_with_env():
    store = VersionStore()
    e1 = add_version(store, label="a", env={"K": "v1"})
    e2 = add_version(store, label="b", env={"K": "v2"})
    assert e1.checksum != e2.checksum


def test_save_and_load_roundtrip(tmp_path):
    path = str(tmp_path / "versions.json")
    store = VersionStore()
    add_version(store, label="first", env=_env())
    add_version(store, label="second", env=_env({"X": "y"}))
    save_versions(path, store)
    loaded = load_versions(path)
    assert len(loaded) == 2
    assert loaded.get(1).label == "first"
    assert loaded.get(2).label == "second"


def test_get_returns_none_for_missing_version():
    store = VersionStore()
    add_version(store, label="only", env=_env())
    assert store.get(99) is None


def test_latest_returns_last_entry():
    store = VersionStore()
    add_version(store, label="a", env=_env())
    add_version(store, label="b", env=_env())
    assert store.latest().label == "b"


def test_version_summary_empty():
    store = VersionStore()
    assert version_summary(store) == "No versions recorded."


def test_version_summary_lists_versions():
    store = VersionStore()
    add_version(store, label="alpha", env=_env())
    add_version(store, label="beta", env=_env({"NEW": "1"}))
    summary = version_summary(store)
    assert "v1" in summary
    assert "alpha" in summary
    assert "v2" in summary
    assert "beta" in summary


def test_save_creates_parent_dirs(tmp_path):
    path = str(tmp_path / "sub" / "dir" / "versions.json")
    store = VersionStore()
    add_version(store, label="x", env=_env())
    save_versions(path, store)
    loaded = load_versions(path)
    assert len(loaded) == 1
