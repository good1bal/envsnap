"""Compute intersection of environment snapshots."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class IntersectResult:
    """Result of intersecting two or more snapshots."""
    common: Dict[str, str]
    agreed: Dict[str, str]  # keys present in all with identical values
    conflicted: Dict[str, List[str]]  # key -> list of differing values

    def __repr__(self) -> str:
        return (
            f"IntersectResult(common={len(self.common)}, "
            f"agreed={len(self.agreed)}, conflicted={len(self.conflicted)})"
        )


def intersect(snapshots: List[Dict[str, str]]) -> IntersectResult:
    """Return keys present in ALL snapshots, noting value agreement."""
    if not snapshots:
        return IntersectResult(common={}, agreed={}, conflicted={})

    common_keys = set(snapshots[0].keys())
    for snap in snapshots[1:]:
        common_keys &= set(snap.keys())

    agreed: Dict[str, str] = {}
    conflicted: Dict[str, List[str]] = {}

    for key in sorted(common_keys):
        values = [snap[key] for snap in snapshots]
        if len(set(values)) == 1:
            agreed[key] = values[0]
        else:
            conflicted[key] = values

    common = {**agreed, **{k: conflicted[k][0] for k in conflicted}}
    return IntersectResult(common=common, agreed=agreed, conflicted=conflicted)


def intersect_summary(result: IntersectResult) -> str:
    lines = [
        f"Common keys : {len(result.common)}",
        f"  Agreed    : {len(result.agreed)}",
        f"  Conflicted: {len(result.conflicted)}",
    ]
    for key, vals in sorted(result.conflicted.items()):
        lines.append(f"    {key}: {' | '.join(vals)}")
    return "\n".join(lines)
