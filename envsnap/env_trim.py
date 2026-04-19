"""Trim keys and/or values in a snapshot."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class TrimResult:
    snapshot: Dict[str, str]
    trimmed_keys: List[str] = field(default_factory=list)
    trimmed_values: List[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return (
            f"TrimResult(keys_trimmed={len(self.trimmed_keys)}, "
            f"values_trimmed={len(self.trimmed_values)})"
        )


def trim_keys(
    snapshot: Dict[str, str],
    fn: Optional[Callable[[str], str]] = None,
) -> TrimResult:
    """Strip whitespace (or apply fn) to all keys."""
    clean = fn or str.strip
    result: Dict[str, str] = {}
    trimmed: List[str] = []
    for k, v in snapshot.items():
        new_k = clean(k)
        if new_k != k:
            trimmed.append(k)
        result[new_k] = v
    return TrimResult(snapshot=result, trimmed_keys=trimmed)


def trim_values(
    snapshot: Dict[str, str],
    keys: Optional[List[str]] = None,
    fn: Optional[Callable[[str], str]] = None,
) -> TrimResult:
    """Strip whitespace (or apply fn) to values, optionally limited to *keys*."""
    clean = fn or str.strip
    result: Dict[str, str] = dict(snapshot)
    trimmed: List[str] = []
    targets = keys if keys is not None else list(snapshot.keys())
    for k in targets:
        if k not in snapshot:
            continue
        new_v = clean(snapshot[k])
        if new_v != snapshot[k]:
            trimmed.append(k)
        result[k] = new_v
    return TrimResult(snapshot=result, trimmed_values=trimmed)


def trim_summary(result: TrimResult) -> str:
    lines = [f"Keys trimmed  : {len(result.trimmed_keys)}"]
    if result.trimmed_keys:
        lines += [f"  - {k}" for k in result.trimmed_keys]
    lines.append(f"Values trimmed: {len(result.trimmed_values)}")
    if result.trimmed_values:
        lines += [f"  - {k}" for k in result.trimmed_values]
    return "\n".join(lines)
