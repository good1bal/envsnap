"""Build a sequential diff timeline from a history of snapshots."""

from __future__ import annotations

from typing import List, Optional

from envsnap.diff import DiffResult, compare
from envsnap.history import load_history


def build_timeline(
    path: Optional[str] = None,
) -> List[dict]:
    """Return list of diffs between consecutive snapshots in history.

    Each entry is::

        {
            "from": label_a,
            "to":   label_b,
            "diff": DiffResult,
        }
    """
    history = load_history(path)
    if len(history) < 2:
        return []

    timeline = []
    for prev, curr in zip(history, history[1:]):
        diff = compare(prev, curr)
        timeline.append(
            {
                "from": prev.get("label", ""),
                "to": curr.get("label", ""),
                "diff": diff,
            }
        )
    return timeline


def timeline_summary(path: Optional[str] = None) -> List[str]:
    """Return human-readable summary lines for each step in the timeline."""
    from envsnap.diff import summary as diff_summary

    lines = []
    for step in build_timeline(path):
        header = f"{step['from']} -> {step['to']}"
        body = diff_summary(step["diff"])
        lines.append(f"{header}\n{body}")
    return lines
