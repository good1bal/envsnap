"""Tests for VersionEntry and VersionStore repr / edge cases."""
from __future__ import annotations

from envsnap.env_version import VersionEntry, VersionStore, add_version


def _entry(version: int = 1, label: str = "test") -> VersionEntry:
    return VersionEntry(version=version, label=label, checksum="abc123def456", env={"K": "v"})


def test_version_entry_attributes():
    e = _entry()
    assert e.version == 1
    assert e.label == "test"
    assert e.checksum == "abc123def456"
    assert e.env == {"K": "v"}


def test_version_store_len_empty():
    store = VersionStore()
    assert len(store) == 0


def test_version_store_len_after_add():
    store = VersionStore()
    add_version(store, label="a", env={"X": "1"})
    add_version(store, label="b", env={"X": "2"})
    assert len(store) == 2


def test_version_store_get_by_version():
    store = VersionStore()
    add_version(store, label="first", env={"A": "1"})
    add_version(store, label="second", env={"B": "2"})
    assert store.get(1).label == "first"
    assert store.get(2).label == "second"


def test_version_entry_env_is_copy():
    original = {"A": "1", "B": "2"}
    store = VersionStore()
    entry = add_version(store, label="snap", env=original)
    original["C"] = "mutated"
    assert "C" not in entry.env


def test_version_numbers_are_sequential():
    store = VersionStore()
    entries = [add_version(store, label=f"v{i}", env={"K": str(i)}) for i in range(5)]
    assert [e.version for e in entries] == [1, 2, 3, 4, 5]
