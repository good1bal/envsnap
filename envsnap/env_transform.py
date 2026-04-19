"""Apply value transformations to snapshot keys."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class TransformResult:
    original: Dict[str, str]
    transformed: Dict[str, str]
    applied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return (
            f"TransformResult(applied={len(self.applied)}, skipped={len(self.skipped)})"
        )


def apply_transform(
    snapshot: Dict[str, str],
    fn: Callable[[str], str],
    keys: Optional[List[str]] = None,
) -> TransformResult:
    """Apply fn to values of selected keys (all keys if keys is None)."""
    target_keys = keys if keys is not None else list(snapshot.keys())
    transformed = dict(snapshot)
    applied: List[str] = []
    skipped: List[str] = []
    for k in target_keys:
        if k not in snapshot:
            skipped.append(k)
            continue
        try:
            transformed[k] = fn(snapshot[k])
            applied.append(k)
        except Exception:
            skipped.append(k)
    return TransformResult(
        original=dict(snapshot),
        transformed=transformed,
        applied=applied,
        skipped=skipped,
    )


def uppercase_values(snapshot: Dict[str, str], keys: Optional[List[str]] = None) -> TransformResult:
    return apply_transform(snapshot, str.upper, keys)


def lowercase_values(snapshot: Dict[str, str], keys: Optional[List[str]] = None) -> TransformResult:
    return apply_transform(snapshot, str.lower, keys)


def strip_values(snapshot: Dict[str, str], keys: Optional[List[str]] = None) -> TransformResult:
    return apply_transform(snapshot, str.strip, keys)


def transform_summary(result: TransformResult) -> str:
    lines = [
        f"Applied : {len(result.applied)}",
        f"Skipped : {len(result.skipped)}",
    ]
    if result.skipped:
        lines.append("Skipped keys: " + ", ".join(result.skipped))
    return "\n".join(lines)
