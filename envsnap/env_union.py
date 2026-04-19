"""Union of multiple snapshots — merge all keys, resolving conflicts by strategy."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Literal

Strategy = Literal["first", "last", "error"]


@dataclass
class UnionResult:
    env: Dict[str, str]
    sources: Dict[str, str]  # key -> label of snapshot it came from
    conflicts: Dict[str, List[str]]  # key -> list of labels that disagreed

    def __repr__(self) -> str:
        return (
            f"UnionResult(keys={len(self.env)}, "
            f"conflicts={len(self.conflicts)})"
        )


class UnionConflict(Exception):
    def __init__(self, key: str, labels: List[str]):
        self.key = key
        self.labels = labels
        super().__init__(f"Conflict on key '{key}' across: {', '.join(labels)}")


def union(
    snapshots: List[Dict],
    strategy: Strategy = "first",
) -> UnionResult:
    """Combine multiple snapshots into one.

    strategy:
      'first' — keep value from the first snapshot that defines the key
      'last'  — keep value from the last snapshot that defines the key
      'error' — raise UnionConflict if any key has differing values
    """
    env: Dict[str, str] = {}
    sources: Dict[str, str] = {}
    conflicts: Dict[str, List[str]] = {}

    for snap in snapshots:
        label = snap.get("label", "unknown")
        snap_env: Dict[str, str] = snap.get("env", {})
        for k, v in snap_env.items():
            if k not in env:
                env[k] = v
                sources[k] = label
            elif env[k] != v:
                if strategy == "error":
                    raise UnionConflict(k, [sources[k], label])
                conflict_labels = conflicts.setdefault(k, [sources[k]])
                if label not in conflict_labels:
                    conflict_labels.append(label)
                if strategy == "last":
                    env[k] = v
                    sources[k] = label

    return UnionResult(env=env, sources=sources, conflicts=conflicts)


def union_summary(result: UnionResult) -> str:
    lines = [
        f"Total keys : {len(result.env)}",
        f"Conflicts  : {len(result.conflicts)}",
    ]
    for key, labels in result.conflicts.items():
        lines.append(f"  {key}: {', '.join(labels)}")
    return "\n".join(lines)
