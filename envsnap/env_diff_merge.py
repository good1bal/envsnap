"""Merge two snapshots using diff-awareness: prefer changed values from source."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envsnap.diff import compare


@dataclass
class DiffMergeResult:
    env: Dict[str, str]
    applied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"DiffMergeResult(applied={len(self.applied)}, "
            f"skipped={len(self.skipped)}, conflicts={len(self.conflicts)})"
        )


def diff_merge(
    base: Dict[str, str],
    source: Dict[str, str],
    target: Dict[str, str],
    *,
    overwrite_unchanged: bool = True,
    raise_on_conflict: bool = False,
) -> DiffMergeResult:
    """Three-way diff-aware merge.

    Keys changed in *source* relative to *base* are promoted into *target*.
    If the same key was also changed in *target* relative to *base*, that is a
    conflict.  By default conflicts are recorded but the *target* value wins.
    """
    base_to_source = compare(base, source)
    base_to_target = compare(base, target)

    changed_in_source = {
        e.key: e.new_value
        for e in base_to_source.changed
    }
    added_in_source = {
        e.key: e.new_value
        for e in base_to_source.added
    }
    changed_in_target = {e.key for e in base_to_target.changed}

    result_env: Dict[str, str] = dict(target)
    applied: List[str] = []
    skipped: List[str] = []
    conflicts: List[str] = []

    for key, value in {**changed_in_source, **added_in_source}.items():
        if key in changed_in_target:
            conflicts.append(key)
            if raise_on_conflict:
                raise ValueError(f"Merge conflict on key: {key!r}")
            # target value wins — skip applying source change
            skipped.append(key)
            continue
        if key in result_env and not overwrite_unchanged:
            skipped.append(key)
            continue
        result_env[key] = value
        applied.append(key)

    return DiffMergeResult(
        env=result_env,
        applied=sorted(applied),
        skipped=sorted(skipped),
        conflicts=sorted(conflicts),
    )


def diff_merge_summary(result: DiffMergeResult) -> str:
    lines = [
        f"Applied : {len(result.applied)}",
        f"Skipped : {len(result.skipped)}",
        f"Conflicts: {len(result.conflicts)}",
    ]
    if result.conflicts:
        lines.append("Conflict keys: " + ", ".join(result.conflicts))
    return "\n".join(lines)
