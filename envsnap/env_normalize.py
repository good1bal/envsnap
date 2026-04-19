"""Normalize environment variable keys and values."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class NormalizeResult:
    original: Dict[str, str]
    normalized: Dict[str, str]
    renamed: Dict[str, str] = field(default_factory=dict)   # old_key -> new_key
    transformed: Dict[str, str] = field(default_factory=dict)  # key -> new_value

    def __repr__(self) -> str:
        return (
            f"NormalizeResult(renamed={len(self.renamed)}, "
            f"transformed={len(self.transformed)})"
        )


def normalize_keys(
    snap: Dict[str, str],
    fn: Callable[[str], str] = str.upper,
) -> NormalizeResult:
    """Apply *fn* to every key; detect renames."""
    normalized: Dict[str, str] = {}
    renamed: Dict[str, str] = {}
    for k, v in snap.items():
        new_k = fn(k)
        normalized[new_k] = v
        if new_k != k:
            renamed[k] = new_k
    return NormalizeResult(original=snap, normalized=normalized, renamed=renamed)


def normalize_values(
    snap: Dict[str, str],
    fn: Callable[[str], str] = str.strip,
    keys: Optional[List[str]] = None,
) -> NormalizeResult:
    """Apply *fn* to values; optionally restrict to *keys*."""
    normalized = dict(snap)
    transformed: Dict[str, str] = {}
    targets = keys if keys is not None else list(snap.keys())
    for k in targets:
        if k not in snap:
            continue
        new_v = fn(snap[k])
        normalized[k] = new_v
        if new_v != snap[k]:
            transformed[k] = new_v
    return NormalizeResult(
        original=snap,
        normalized=normalized,
        transformed=transformed,
    )


def normalize_summary(result: NormalizeResult) -> str:
    lines = [f"Renamed keys : {len(result.renamed)}"]
    for old, new in result.renamed.items():
        lines.append(f"  {old!r} -> {new!r}")
    lines.append(f"Transformed values: {len(result.transformed)}")
    for k, v in result.transformed.items():
        lines.append(f"  {k}: {result.original[k]!r} -> {v!r}")
    return "\n".join(lines)
