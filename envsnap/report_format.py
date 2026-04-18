"""Format a CompareReport for terminal or file output."""

from __future__ import annotations

from typing import List

from envsnap.compare_report import CompareReport, ReportEntry

STATUS_SYMBOLS = {
    "added": "+",
    "removed": "-",
    "changed": "~",
    "unchanged": " ",
}


def _fmt_entry(entry: ReportEntry) -> str:
    sym = STATUS_SYMBOLS.get(entry.status, "?")
    if entry.status == "added":
        return f"  {sym} {entry.key}={entry.new_value}"
    if entry.status == "removed":
        return f"  {sym} {entry.key}={entry.old_value}"
    if entry.status == "changed":
        return f"  {sym} {entry.key}: {entry.old_value!r} -> {entry.new_value!r}"
    return f"  {sym} {entry.key}={entry.old_value}"


def format_report(report: CompareReport, show_unchanged: bool = False) -> str:
    lines: List[str] = [
        f"Comparing '{report.label_a}' -> '{report.label_b}'",
        "-" * 48,
    ]

    groups = ["added", "removed", "changed"]
    if show_unchanged:
        groups.append("unchanged")

    for status in groups:
        entries = report.by_status(status)
        if entries:
            lines.append(f"{status.upper()} ({len(entries)}):")
            lines.extend(_fmt_entry(e) for e in entries)

    if not report.has_changes:
        lines.append("No changes detected.")

    added = len(report.by_status("added"))
    removed = len(report.by_status("removed"))
    changed = len(report.by_status("changed"))
    lines.append("-" * 48)
    lines.append(f"Summary: +{added} added  -{removed} removed  ~{changed} changed")

    return "\n".join(lines)
