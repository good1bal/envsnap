"""Merge multiple snapshots into a single unified snapshot."""

from __future__ import annotations

from typing import Any

from envsnap.snapshot import _checksum


class MergeConflict(Exception):
    """Raised when snapshots have conflicting values for the same key."""


def merge(
    *snapshots: dict[str, Any],
    on_conflict: str = "raise",
    label: str = "merged",
) -> dict[str, Any]:
    """Merge multiple snapshots into one.

    Args:
        *snapshots: Snapshot dicts as returned by capture() / load().
        on_conflict: One of 'raise', 'first', 'last'.
        label: Label to assign to the merged snapshot.

    Returns:
        A new snapshot dict with merged variables.
    """
    if not snapshots:
        raise ValueError("At least one snapshot is required.")

    merged_vars: dict[str, str] = {}
    conflicts: list[str] = []

    for snap in snapshots:
        variables = snap.get("variables", {})
        for key, value in variables.items():
            if key in merged_vars and merged_vars[key] != value:
                if on_conflict == "raise":
                    conflicts.append(key)
                elif on_conflict == "last":
                    merged_vars[key] = value
                # 'first' — keep existing value
            else:
                merged_vars[key] = value

    if conflicts:
        raise MergeConflict(
            f"Conflicting values for keys: {', '.join(sorted(conflicts))}"
        )

    return {
        "label": label,
        "variables": merged_vars,
        "checksum": _checksum(merged_vars),
    }


def merge_labels(*snapshots: dict[str, Any]) -> list[str]:
    """Return the list of labels from the snapshots being merged."""
    return [snap.get("label", "unknown") for snap in snapshots]
