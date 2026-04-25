"""Export diff results to various formats (JSON, CSV, Markdown)."""
from __future__ import annotations

import csv
import io
import json
from typing import List

from envsnap.diff import DiffResult


def to_json(result: DiffResult, indent: int = 2) -> str:
    """Serialise a DiffResult to a JSON string."""
    data = {
        "label_a": result.label_a,
        "label_b": result.label_b,
        "added": result.added,
        "removed": result.removed,
        "changed": [
            {"key": k, "before": before, "after": after}
            for k, (before, after) in result.changed.items()
        ],
        "unchanged": list(result.unchanged.keys()),
    }
    return json.dumps(data, indent=indent, sort_keys=True)


def to_csv(result: DiffResult) -> str:
    """Serialise a DiffResult to a CSV string with columns: status, key, before, after."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["status", "key", "before", "after"])

    for key in sorted(result.added):
        writer.writerow(["added", key, "", result.added[key]])

    for key in sorted(result.removed):
        writer.writerow(["removed", key, result.removed[key], ""])

    for key in sorted(result.changed):
        before, after = result.changed[key]
        writer.writerow(["changed", key, before, after])

    for key in sorted(result.unchanged):
        writer.writerow(["unchanged", key, result.unchanged[key], result.unchanged[key]])

    return buf.getvalue()


def to_markdown(result: DiffResult) -> str:
    """Serialise a DiffResult to a Markdown table."""
    lines: List[str] = []
    label_a = result.label_a or "A"
    label_b = result.label_b or "B"

    lines.append(f"## Diff: `{label_a}` → `{label_b}`")
    lines.append("")
    lines.append("| Status | Key | Before | After |")
    lines.append("|--------|-----|--------|-------|")

    for key in sorted(result.added):
        lines.append(f"| added | `{key}` | | `{result.added[key]}` |")

    for key in sorted(result.removed):
        lines.append(f"| removed | `{key}` | `{result.removed[key]}` | |")

    for key in sorted(result.changed):
        before, after = result.changed[key]
        lines.append(f"| changed | `{key}` | `{before}` | `{after}` |")

    for key in sorted(result.unchanged):
        v = result.unchanged[key]
        lines.append(f"| unchanged | `{key}` | `{v}` | `{v}` |")

    return "\n".join(lines) + "\n"
