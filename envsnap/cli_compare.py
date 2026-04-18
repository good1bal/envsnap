"""CLI commands for snapshot comparison reports."""

from __future__ import annotations

import sys
from typing import Optional

from envsnap.snapshot import load
from envsnap.compare_report import build_report
from envsnap.report_format import format_report
from envsnap.history import load_history, get_snapshot


def cmd_compare(
    path_a: Optional[str] = None,
    path_b: Optional[str] = None,
    label_a: Optional[str] = None,
    label_b: Optional[str] = None,
    history_file: Optional[str] = None,
    redact: bool = True,
    show_unchanged: bool = False,
) -> int:
    """Compare two snapshots and print a formatted report. Returns exit code."""
    snap_a = _resolve_snapshot(path_a, label_a, history_file, "first")
    snap_b = _resolve_snapshot(path_b, label_b, history_file, "second")

    if snap_a is None or snap_b is None:
        return 1

    report = build_report(snap_a, snap_b, redact_sensitive=redact, include_unchanged=show_unchanged)
    print(format_report(report, show_unchanged=show_unchanged))
    return 0 if not report.has_changes else 1


def cmd_compare_files(path_a: str, path_b: str, **kwargs) -> int:
    """Convenience wrapper to compare two snapshot files directly."""
    return cmd_compare(path_a=path_a, path_b=path_b, **kwargs)


def _resolve_snapshot(
    path: Optional[str],
    label: Optional[str],
    history_file: Optional[str],
    which: str,
) -> Optional[dict]:
    if path:
        try:
            return load(path)
        except FileNotFoundError:
            print(f"Error: snapshot file not found: {path}", file=sys.stderr)
            return None

    if label:
        history = load_history(history_file) if history_file else load_history()
        snap = get_snapshot(history, label)
        if snap is None:
            print(f"Error: label '{label}' not found in history.", file=sys.stderr)
        return snap

    print(f"Error: provide --file or --label for {which} snapshot.", file=sys.stderr)
    return None
