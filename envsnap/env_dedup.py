"""Detect and remove duplicate values across environment variable keys."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DedupResult:
    snapshot: Dict[str, str]
    duplicates: Dict[str, List[str]]  # value -> list of keys sharing it
    removed: List[str]

    def __repr__(self) -> str:
        return (
            f"DedupResult(kept={len(self.snapshot)}, "
            f"duplicate_groups={len(self.duplicates)}, removed={len(self.removed)})"
        )


def find_duplicates(env: Dict[str, str]) -> Dict[str, List[str]]:
    """Return mapping of value -> keys that share it (only where len > 1)."""
    from collections import defaultdict
    index: Dict[str, List[str]] = defaultdict(list)
    for k, v in env.items():
        index[v].append(k)
    return {v: keys for v, keys in index.items() if len(keys) > 1}


def dedup_snapshot(
    env: Dict[str, str],
    keep: str = "first",
    ignore_empty: bool = True,
) -> DedupResult:
    """Remove keys with duplicate values, keeping one representative per value.

    Args:
        env: The environment snapshot dict.
        keep: 'first' keeps the alphabetically first key; 'last' keeps the last.
        ignore_empty: If True, empty-string values are not considered duplicates.
    """
    duplicates = find_duplicates(env)
    if ignore_empty:
        duplicates = {v: keys for v, keys in duplicates.items() if v != ""}

    removed: List[str] = []
    result = dict(env)

    for value, keys in duplicates.items():
        sorted_keys = sorted(keys)
        if keep == "last":
            to_remove = sorted_keys[:-1]
        else:
            to_remove = sorted_keys[1:]
        for k in to_remove:
            result.pop(k, None)
            removed.append(k)

    return DedupResult(snapshot=result, duplicates=duplicates, removed=sorted(removed))


def dedup_summary(result: DedupResult) -> str:
    if not result.removed:
        return "No duplicate values found."
    lines = [f"Removed {len(result.removed)} duplicate key(s):"]
    for value, keys in result.duplicates.items():
        kept = [k for k in sorted(keys) if k not in result.removed]
        display_val = repr(value[:40] + "..." if len(value) > 40 else value)
        lines.append(f"  {display_val}: kept {kept[0]!r}, removed {[k for k in keys if k in result.removed]}")
    return "\n".join(lines)
