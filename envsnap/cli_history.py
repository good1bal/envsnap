"""CLI helpers for history and timeline sub-commands."""

from __future__ import annotations

from typing import Optional

from envsnap.history import (
    append_snapshot,
    latest_snapshot,
    list_labels,
    load_history,
)
from envsnap.snapshot import capture
from envsnap.timeline import build_timeline, timeline_summary


def cmd_record(
    label: str,
    history_file: Optional[str] = None,
    exclude_prefixes: Optional[list] = None,
) -> dict:
    """Capture current environment and append to history."""
    snap = capture(label=label, exclude_prefixes=exclude_prefixes or [])
    append_snapshot(snap, history_file)
    return snap


def cmd_log(history_file: Optional[str] = None) -> str:
    """Return formatted list of recorded labels."""
    labels = list_labels(history_file)
    if not labels:
        return "No snapshots recorded."
    lines = [f"  [{i}] {lbl}" for i, lbl in enumerate(labels)]
    return "Snapshot history:\n" + "\n".join(lines)


def cmd_timeline(history_file: Optional[str] = None) -> str:
    """Return full timeline summary as a single string."""
    summaries = timeline_summary(history_file)
    if not summaries:
        return "Not enough snapshots to build a timeline."
    return "\n\n".join(summaries)


def cmd_show(label: str, history_file: Optional[str] = None) -> str:
    """Return formatted vars for a named snapshot."""
    from envsnap.history import get_snapshot

    snap = get_snapshot(label, history_file)
    if snap is None:
        return f"Snapshot '{label}' not found."
    lines = [f"  {k}={v}" for k, v in sorted(snap.get("vars", {}).items())]
    header = f"Snapshot: {snap.get('label')}  checksum={snap.get('checksum', '')[:8]}"
    return header + "\n" + "\n".join(lines)
