"""Audit log: track when snapshots were taken, compared, or validated."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

DEFAULT_AUDIT_FILE = ".envsnap_audit.json"


@dataclass
class AuditEntry:
    action: str          # e.g. "capture", "compare", "validate", "watch"
    label: Optional[str]
    timestamp: str
    details: dict

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "AuditEntry":
        return AuditEntry(
            action=d["action"],
            label=d.get("label"),
            timestamp=d["timestamp"],
            details=d.get("details", {}),
        )


def _audit_path(path: Optional[str] = None) -> Path:
    return Path(path or os.environ.get("ENVSNAP_AUDIT_FILE", DEFAULT_AUDIT_FILE))


def load_audit(path: Optional[str] = None) -> List[AuditEntry]:
    p = _audit_path(path)
    if not p.exists():
        return []
    with p.open() as f:
        data = json.load(f)
    return [AuditEntry.from_dict(e) for e in data]


def save_audit(entries: List[AuditEntry], path: Optional[str] = None) -> None:
    p = _audit_path(path)
    with p.open("w") as f:
        json.dump([e.to_dict() for e in entries], f, indent=2)


def record(action: str, label: Optional[str] = None, details: Optional[dict] = None,
           path: Optional[str] = None) -> AuditEntry:
    entry = AuditEntry(
        action=action,
        label=label,
        timestamp=datetime.now(timezone.utc).isoformat(),
        details=details or {},
    )
    entries = load_audit(path)
    entries.append(entry)
    save_audit(entries, path)
    return entry


def recent(n: int = 10, path: Optional[str] = None) -> List[AuditEntry]:
    return load_audit(path)[-n:]
