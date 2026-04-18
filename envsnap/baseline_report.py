"""Formatting helpers for baseline diff output."""

from __future__ import annotations

from typing import Dict


def format_baseline_diff(result: Dict, label_a: str = "baseline", label_b: str = "current") -> str:
    lines = [f"Baseline diff: {label_a} → {label_b}"]
    lines.append("-" * 40)

    added = result.get("added", {})
    removed = result.get("removed", {})
    changed = result.get("changed", {})
    unchanged = result.get("unchanged", {})

    if added:
        lines.append(f"Added ({len(added)}):")
        for k, v in sorted(added.items()):
            lines.append(f"  + {k}={v}")

    if removed:
        lines.append(f"Removed ({len(removed)}):")
        for k, v in sorted(removed.items()):
            lines.append(f"  - {k}={v}")

    if changed:
        lines.append(f"Changed ({len(changed)}):")
        for k, (old, new) in sorted(changed.items()):
            lines.append(f"  ~ {k}: {old!r} → {new!r}")

    if not added and not removed and not changed:
        lines.append("No changes detected.")
    else:
        total = len(added) + len(removed) + len(changed)
        lines.append("-" * 40)
        lines.append(f"Total changes: {total}  (unchanged: {len(unchanged)})")

    return "\n".join(lines)


def baseline_status_line(result: Dict) -> str:
    """One-line status suitable for CI output."""
    counts = [
        len(result.get("added", {})),
        len(result.get("removed", {})),
        len(result.get("changed", {})),
    ]
    total = sum(counts)
    if total == 0:
        return "baseline: OK (no changes)"
    a, r, c = counts
    return f"baseline: CHANGED (+{a} -{r} ~{c})"
