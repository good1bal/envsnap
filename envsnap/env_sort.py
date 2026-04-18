"""Utilities for sorting environment variable snapshots."""
from __future__ import annotations

from typing import Dict, List, Literal

SortKey = Literal["key", "value", "length"]


def sort_snapshot(
    env: Dict[str, str],
    by: SortKey = "key",
    reverse: bool = False,
) -> Dict[str, str]:
    """Return a new dict with keys sorted by the given strategy."""
    if by == "key":
        pairs = sorted(env.items(), key=lambda kv: kv[0].lower(), reverse=reverse)
    elif by == "value":
        pairs = sorted(env.items(), key=lambda kv: kv[1].lower(), reverse=reverse)
    elif by == "length":
        pairs = sorted(env.items(), key=lambda kv: len(kv[0]), reverse=reverse)
    else:
        raise ValueError(f"Unknown sort key: {by!r}. Choose from 'key', 'value', 'length'.")
    return dict(pairs)


def sort_keys(env: Dict[str, str], by: SortKey = "key", reverse: bool = False) -> List[str]:
    """Return a sorted list of keys from the snapshot."""
    return list(sort_snapshot(env, by=by, reverse=reverse).keys())


def group_sorted(
    env: Dict[str, str],
    by: SortKey = "key",
    reverse: bool = False,
) -> Dict[str, Dict[str, str]]:
    """Group keys by first character (after sorting)."""
    sorted_env = sort_snapshot(env, by=by, reverse=reverse)
    groups: Dict[str, Dict[str, str]] = {}
    for k, v in sorted_env.items():
        bucket = k[0].upper() if k else "_"
        groups.setdefault(bucket, {})[k] = v
    return groups
