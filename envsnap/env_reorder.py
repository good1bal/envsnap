"""Reorder keys in a snapshot according to a given key order or sort strategy."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class ReorderResult:
    env: Dict[str, str]
    original_order: List[str]
    new_order: List[str]

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"ReorderResult(keys={len(self.env)}, "
            f"changed={self.original_order != self.new_order})"
        )


def reorder_by_list(
    snapshot: Dict[str, str],
    key_order: List[str],
    *,
    append_remaining: bool = True,
) -> ReorderResult:
    """Reorder snapshot keys according to *key_order*.

    Keys not listed in *key_order* are appended at the end when
    *append_remaining* is True, otherwise they are dropped.
    """
    original_order = list(snapshot.keys())
    ordered: Dict[str, str] = {}

    for key in key_order:
        if key in snapshot:
            ordered[key] = snapshot[key]

    if append_remaining:
        for key in snapshot:
            if key not in ordered:
                ordered[key] = snapshot[key]

    return ReorderResult(
        env=ordered,
        original_order=original_order,
        new_order=list(ordered.keys()),
    )


def reorder_by_fn(
    snapshot: Dict[str, str],
    key_fn: Callable[[str], object],
    *,
    reverse: bool = False,
) -> ReorderResult:
    """Reorder snapshot keys using a sort key function."""
    original_order = list(snapshot.keys())
    sorted_keys = sorted(snapshot.keys(), key=key_fn, reverse=reverse)
    ordered = {k: snapshot[k] for k in sorted_keys}
    return ReorderResult(
        env=ordered,
        original_order=original_order,
        new_order=sorted_keys,
    )


def reorder_summary(result: ReorderResult) -> str:
    """Return a human-readable summary of a reorder operation."""
    if result.original_order == result.new_order:
        return f"Order unchanged ({len(result.env)} keys)."
    moved = sum(
        1
        for i, (a, b) in enumerate(
            zip(result.original_order, result.new_order)
        )
        if a != b
    )
    return (
        f"Reordered {len(result.env)} keys; "
        f"{moved} position(s) changed."
    )
