"""High-level summary statistics for environment diffs."""
from dataclasses import dataclass, field
from typing import List
from envsnap.diff import DiffResult, compare


@dataclass
class DiffStats:
    added: int = 0
    removed: int = 0
    changed: int = 0
    unchanged: int = 0

    @property
    def total_changes(self) -> int:
        return self.added + self.removed + self.changed

    @property
    def total_keys(self) -> int:
        return self.total_changes + self.unchanged


@dataclass
class DiffSummaryReport:
    label_a: str
    label_b: str
    stats: DiffStats
    added_keys: List[str] = field(default_factory=list)
    removed_keys: List[str] = field(default_factory=list)
    changed_keys: List[str] = field(default_factory=list)


def compute_stats(result: DiffResult) -> DiffStats:
    return DiffStats(
        added=len(result.added),
        removed=len(result.removed),
        changed=len(result.changed),
        unchanged=len(result.unchanged),
    )


def build_diff_summary(snap_a: dict, snap_b: dict) -> DiffSummaryReport:
    result = compare(snap_a, snap_b)
    stats = compute_stats(result)
    return DiffSummaryReport(
        label_a=snap_a.get("label", "snapshot_a"),
        label_b=snap_b.get("label", "snapshot_b"),
        stats=stats,
        added_keys=sorted(result.added.keys()),
        removed_keys=sorted(result.removed.keys()),
        changed_keys=sorted(result.changed.keys()),
    )


def format_diff_summary(report: DiffSummaryReport) -> str:
    lines = [
        f"Diff: {report.label_a} → {report.label_b}",
        f"  Added:     {report.stats.added}",
        f"  Removed:   {report.stats.removed}",
        f"  Changed:   {report.stats.changed}",
        f"  Unchanged: {report.stats.unchanged}",
        f"  Total keys: {report.stats.total_keys}",
    ]
    if report.added_keys:
        lines.append("  + " + ", ".join(report.added_keys))
    if report.removed_keys:
        lines.append("  - " + ", ".join(report.removed_keys))
    if report.changed_keys:
        lines.append("  ~ " + ", ".join(report.changed_keys))
    return "\n".join(lines)
