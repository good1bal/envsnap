"""Attach annotations to diff results for richer reporting."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envsnap.diff import DiffResult


@dataclass
class AnnotatedEntry:
    key: str
    status: str  # added | removed | changed | unchanged
    old_value: Optional[str]
    new_value: Optional[str]
    note: str = ""
    tags: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"AnnotatedEntry(key={self.key!r}, status={self.status!r}, "
            f"note={self.note!r}, tags={self.tags!r})"
        )


@dataclass
class AnnotatedDiff:
    label_a: str
    label_b: str
    entries: List[AnnotatedEntry] = field(default_factory=list)

    def by_status(self, status: str) -> List[AnnotatedEntry]:
        return [e for e in self.entries if e.status == status]

    def tagged(self, tag: str) -> List[AnnotatedEntry]:
        return [e for e in self.entries if tag in e.tags]

    def __len__(self) -> int:
        return len(self.entries)


def annotate_diff(
    result: DiffResult,
    notes: Optional[Dict[str, str]] = None,
    tags: Optional[Dict[str, List[str]]] = None,
) -> AnnotatedDiff:
    """Wrap a DiffResult with per-key notes and tags."""
    notes = notes or {}
    tags = tags or {}

    entries: List[AnnotatedEntry] = []

    for key in result.added:
        entries.append(AnnotatedEntry(
            key=key, status="added",
            old_value=None, new_value=result.snapshot_b.get("env", {}).get(key),
            note=notes.get(key, ""), tags=tags.get(key, []),
        ))

    for key in result.removed:
        entries.append(AnnotatedEntry(
            key=key, status="removed",
            old_value=result.snapshot_a.get("env", {}).get(key), new_value=None,
            note=notes.get(key, ""), tags=tags.get(key, []),
        ))

    for key, (old, new) in result.changed.items():
        entries.append(AnnotatedEntry(
            key=key, status="changed",
            old_value=old, new_value=new,
            note=notes.get(key, ""), tags=tags.get(key, []),
        ))

    for key in result.unchanged:
        entries.append(AnnotatedEntry(
            key=key, status="unchanged",
            old_value=result.snapshot_a.get("env", {}).get(key),
            new_value=result.snapshot_b.get("env", {}).get(key),
            note=notes.get(key, ""), tags=tags.get(key, []),
        ))

    entries.sort(key=lambda e: e.key)

    return AnnotatedDiff(
        label_a=result.snapshot_a.get("label", "a"),
        label_b=result.snapshot_b.get("label", "b"),
        entries=entries,
    )


def annotated_diff_summary(ad: AnnotatedDiff) -> str:
    """Return a compact human-readable summary of an annotated diff."""
    counts = {s: 0 for s in ("added", "removed", "changed", "unchanged")}
    for e in ad.entries:
        counts[e.status] += 1
    noted = sum(1 for e in ad.entries if e.note)
    tagged = sum(1 for e in ad.entries if e.tags)
    return (
        f"{ad.label_a} -> {ad.label_b}: "
        f"+{counts['added']} -{counts['removed']} ~{counts['changed']} "
        f"={counts['unchanged']} | noted={noted} tagged={tagged}"
    )
