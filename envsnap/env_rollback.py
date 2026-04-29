"""Rollback support: revert a snapshot to a previous state from history."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envsnap.snapshot import Snapshot
from envsnap.diff import compare, DiffResult


@dataclass
class RollbackResult:
    """Result of a rollback operation."""
    original: Dict[str, str]
    reverted: Dict[str, str]
    diff: DiffResult
    keys_restored: List[str] = field(default_factory=list)
    keys_removed: List[str] = field(default_factory=list)
    keys_unchanged: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"RollbackResult(restored={len(self.keys_restored)}, "
            f"removed={len(self.keys_removed)}, "
            f"unchanged={len(self.keys_unchanged)})"
        )


def rollback(
    current: Snapshot,
    target: Snapshot,
    keys: Optional[List[str]] = None,
) -> RollbackResult:
    """Revert *current* env to match *target*.

    If *keys* is given, only those keys are rolled back; all others are kept
    from *current*.
    """
    current_env: Dict[str, str] = current.get("env", {})
    target_env: Dict[str, str] = target.get("env", {})

    if keys is not None:
        key_set = set(keys)
    else:
        key_set = set(current_env) | set(target_env)

    reverted: Dict[str, str] = dict(current_env)

    restored: List[str] = []
    removed: List[str] = []
    unchanged: List[str] = []

    for key in sorted(key_set):
        in_current = key in current_env
        in_target = key in target_env

        if in_target:
            if current_env.get(key) != target_env[key]:
                reverted[key] = target_env[key]
                restored.append(key)
            else:
                unchanged.append(key)
        else:
            if in_current:
                del reverted[key]
                removed.append(key)

    new_snap: Snapshot = dict(current)
    new_snap["env"] = reverted

    diff = compare(current, new_snap)

    return RollbackResult(
        original=current_env,
        reverted=reverted,
        diff=diff,
        keys_restored=restored,
        keys_removed=removed,
        keys_unchanged=unchanged,
    )


def rollback_summary(result: RollbackResult) -> str:
    """Return a human-readable summary of a rollback."""
    lines = [
        f"Rollback summary:",
        f"  Restored : {len(result.keys_restored)}",
        f"  Removed  : {len(result.keys_removed)}",
        f"  Unchanged: {len(result.keys_unchanged)}",
    ]
    return "\n".join(lines)
