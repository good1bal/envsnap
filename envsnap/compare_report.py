"""Generate structured comparison reports between two snapshots."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envsnap.diff import DiffResult, compare
from envsnap.redact import redact


@dataclass
class ReportEntry:
    key: str
    status: str  # 'added' | 'removed' | 'changed' | 'unchanged'
    old_value: Optional[str] = None
    new_value: Optional[str] = None


@dataclass
class CompareReport:
    label_a: str
    label_b: str
    entries: List[ReportEntry] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return any(e.status != "unchanged" for e in self.entries)

    def by_status(self, status: str) -> List[ReportEntry]:
        return [e for e in self.entries if e.status == status]


def build_report(
    snap_a: dict,
    snap_b: dict,
    redact_sensitive: bool = True,
    include_unchanged: bool = False,
) -> CompareReport:
    """Build a CompareReport from two snapshot dicts."""
    result: DiffResult = compare(snap_a, snap_b)
    entries: List[ReportEntry] = []

    for key in result.added:
        val = snap_b["vars"][key]
        entries.append(ReportEntry(key=key, status="added", new_value=val))

    for key in result.removed:
        val = snap_a["vars"][key]
        entries.append(ReportEntry(key=key, status="removed", old_value=val))

    for key, (old, new) in result.changed.items():
        entries.append(ReportEntry(key=key, status="changed", old_value=old, new_value=new))

    if include_unchanged:
        for key in result.unchanged:
            val = snap_a["vars"][key]
            entries.append(ReportEntry(key=key, status="unchanged", old_value=val, new_value=val))

    if redact_sensitive:
        for e in entries:
            if e.old_value is not None:
                e.old_value = redact({e.key: e.old_value})[e.key]
            if e.new_value is not None:
                e.new_value = redact({e.key: e.new_value})[e.key]

    entries.sort(key=lambda e: e.key)

    return CompareReport(
        label_a=snap_a.get("label", "a"),
        label_b=snap_b.get("label", "b"),
        entries=entries,
    )
