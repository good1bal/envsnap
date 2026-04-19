"""Filter DiffResult entries by status, key pattern, or custom predicate."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from envsnap.diff import DiffResult


@dataclass
class FilteredDiff:
    original: DiffResult
    entries: List[dict] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.entries)

    def __repr__(self) -> str:  # pragma: no cover
        return f"FilteredDiff(count={len(self)})"


def _iter_entries(result: DiffResult):
    for key in result.added:
        yield {"key": key, "status": "added", "before": None, "after": result.b.get(key)}
    for key in result.removed:
        yield {"key": key, "status": "removed", "before": result.a.get(key), "after": None}
    for key, (before, after) in result.changed.items():
        yield {"key": key, "status": "changed", "before": before, "after": after}
    for key in result.unchanged:
        yield {"key": key, "status": "unchanged", "before": result.a.get(key), "after": result.a.get(key)}


def filter_diff(
    result: DiffResult,
    *,
    statuses: Optional[List[str]] = None,
    key_pattern: Optional[str] = None,
    predicate: Optional[Callable[[dict], bool]] = None,
) -> FilteredDiff:
    """Return a FilteredDiff containing only entries matching all supplied criteria."""
    entries = list(_iter_entries(result))

    if statuses:
        allowed = set(statuses)
        entries = [e for e in entries if e["status"] in allowed]

    if key_pattern:
        rx = re.compile(key_pattern)
        entries = [e for e in entries if rx.search(e["key"])]

    if predicate:
        entries = [e for e in entries if predicate(e)]

    return FilteredDiff(original=result, entries=entries)


def changes_only(result: DiffResult) -> FilteredDiff:
    """Convenience: return only added, removed, and changed entries."""
    return filter_diff(result, statuses=["added", "removed", "changed"])


def filter_diff_summary(fd: FilteredDiff) -> str:
    counts: dict = {}
    for e in fd.entries:
        counts[e["status"]] = counts.get(e["status"], 0) + 1
    parts = [f"{v} {k}" for k, v in sorted(counts.items())]
    return ", ".join(parts) if parts else "no entries"
