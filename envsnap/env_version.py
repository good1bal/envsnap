"""Versioning support for environment snapshots."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envsnap.snapshot import _checksum


@dataclass
class VersionEntry:
    version: int
    label: str
    checksum: str
    env: Dict[str, str]

    def __repr__(self) -> str:  # pragma: no cover
        return f"VersionEntry(version={self.version}, label={self.label!r}, checksum={self.checksum[:8]}...)"


@dataclass
class VersionStore:
    entries: List[VersionEntry] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.entries)

    def latest(self) -> Optional[VersionEntry]:
        return self.entries[-1] if self.entries else None

    def get(self, version: int) -> Optional[VersionEntry]:
        for e in self.entries:
            if e.version == version:
                return e
        return None


def _version_path(store_path: str) -> Path:
    return Path(store_path)


def load_versions(store_path: str) -> VersionStore:
    p = _version_path(store_path)
    if not p.exists():
        return VersionStore()
    data = json.loads(p.read_text())
    entries = [
        VersionEntry(
            version=e["version"],
            label=e["label"],
            checksum=e["checksum"],
            env=e["env"],
        )
        for e in data.get("entries", [])
    ]
    return VersionStore(entries=entries)


def save_versions(store_path: str, store: VersionStore) -> None:
    p = _version_path(store_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "entries": [
            {"version": e.version, "label": e.label, "checksum": e.checksum, "env": e.env}
            for e in store.entries
        ]
    }
    p.write_text(json.dumps(data, indent=2))


def add_version(store: VersionStore, label: str, env: Dict[str, str]) -> VersionEntry:
    next_ver = (store.latest().version + 1) if store.latest() else 1
    entry = VersionEntry(version=next_ver, label=label, checksum=_checksum(env), env=dict(env))
    store.entries.append(entry)
    return entry


def version_summary(store: VersionStore) -> str:
    if not store.entries:
        return "No versions recorded."
    lines = [f"v{e.version}  {e.label}  [{e.checksum[:8]}]" for e in store.entries]
    return "\n".join(lines)
