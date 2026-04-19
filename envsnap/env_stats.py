"""Compute descriptive statistics over snapshot environment variables."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class EnvStats:
    total_keys: int = 0
    unique_values: int = 0
    empty_values: int = 0
    duplicate_values: int = 0
    avg_key_length: float = 0.0
    avg_value_length: float = 0.0
    longest_key: str = ""
    shortest_key: str = ""
    prefix_counts: Dict[str, int] = field(default_factory=dict)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"EnvStats(total={self.total_keys}, empty={self.empty_values}, "
            f"duplicates={self.duplicate_values})"
        )


def compute_stats(env: Dict[str, str], prefix_sep: str = "_") -> EnvStats:
    """Return an EnvStats summary for the given env dict."""
    if not env:
        return EnvStats()

    keys: List[str] = list(env.keys())
    values: List[str] = list(env.values())

    total_keys = len(keys)
    empty_values = sum(1 for v in values if v == "")
    value_counts: Dict[str, int] = {}
    for v in values:
        value_counts[v] = value_counts.get(v, 0) + 1
    unique_values = len(value_counts)
    duplicate_values = sum(1 for cnt in value_counts.values() if cnt > 1)

    avg_key_length = sum(len(k) for k in keys) / total_keys
    avg_value_length = sum(len(v) for v in values) / total_keys
    longest_key = max(keys, key=len)
    shortest_key = min(keys, key=len)

    prefix_counts: Dict[str, int] = {}
    for k in keys:
        if prefix_sep in k:
            prefix = k.split(prefix_sep)[0]
            prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1

    return EnvStats(
        total_keys=total_keys,
        unique_values=unique_values,
        empty_values=empty_values,
        duplicate_values=duplicate_values,
        avg_key_length=round(avg_key_length, 2),
        avg_value_length=round(avg_value_length, 2),
        longest_key=longest_key,
        shortest_key=shortest_key,
        prefix_counts=prefix_counts,
    )


def stats_summary(stats: EnvStats) -> str:
    """Return a human-readable summary string for EnvStats."""
    lines = [
        f"Total keys       : {stats.total_keys}",
        f"Unique values    : {stats.unique_values}",
        f"Empty values     : {stats.empty_values}",
        f"Duplicate values : {stats.duplicate_values}",
        f"Avg key length   : {stats.avg_key_length}",
        f"Avg value length : {stats.avg_value_length}",
        f"Longest key      : {stats.longest_key}",
        f"Shortest key     : {stats.shortest_key}",
    ]
    if stats.prefix_counts:
        lines.append("Prefix counts    :")
        for prefix, count in sorted(stats.prefix_counts.items()):
            lines.append(f"  {prefix}: {count}")
    return "\n".join(lines)
