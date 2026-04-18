"""Tests for envsnap.audit."""
import json
import pytest
from envsnap.audit import (
    AuditEntry, load_audit, save_audit, record, recent, _audit_path
)


@pytest.fixture
def audit_file(tmp_path):
    return str(tmp_path / "audit.json")


def test_load_audit_missing_file_returns_empty(audit_file, tmp_path):
    path = str(tmp_path / "nonexistent.json")
    assert load_audit(path) == []


def test_record_creates_entry(audit_file):
    entry = record("capture", label="prod", details={"keys": 5}, path=audit_file)
    assert entry.action == "capture"
    assert entry.label == "prod"
    assert entry.details == {"keys": 5}
    assert "T" in entry.timestamp  # ISO format


def test_record_persists_to_file(audit_file):
    record("compare", label="staging", path=audit_file)
    entries = load_audit(audit_file)
    assert len(entries) == 1
    assert entries[0].action == "compare"


def test_record_appends_multiple(audit_file):
    record("capture", path=audit_file)
    record("validate", path=audit_file)
    record("watch", path=audit_file)
    entries = load_audit(audit_file)
    assert len(entries) == 3
    assert [e.action for e in entries] == ["capture", "validate", "watch"]


def test_save_and_load_roundtrip(audit_file):
    original = [
        AuditEntry(action="capture", label="dev", timestamp="2024-01-01T00:00:00+00:00", details={"n": 3}),
        AuditEntry(action="compare", label=None, timestamp="2024-01-02T00:00:00+00:00", details={}),
    ]
    save_audit(original, audit_file)
    loaded = load_audit(audit_file)
    assert len(loaded) == 2
    assert loaded[0].action == "capture"
    assert loaded[0].label == "dev"
    assert loaded[1].label is None


def test_recent_returns_last_n(audit_file):
    for i in range(7):
        record("capture", label=str(i), path=audit_file)
    r = recent(3, path=audit_file)
    assert len(r) == 3
    assert r[-1].label == "6"


def test_recent_fewer_than_n(audit_file):
    record("validate", path=audit_file)
    r = recent(10, path=audit_file)
    assert len(r) == 1


def test_entry_to_dict_and_from_dict():
    e = AuditEntry(action="watch", label="prod", timestamp="2024-01-01T00:00:00+00:00", details={"changes": 2})
    d = e.to_dict()
    assert d["action"] == "watch"
    restored = AuditEntry.from_dict(d)
    assert restored.details == {"changes": 2}
