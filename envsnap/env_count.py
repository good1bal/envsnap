"""Count and summarize environment variable keys by various criteria."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CountResult:
    total: int
    by_prefix: Dict[str, int] = field(default_factory=dict)
    empty_values: int = 0
    non_empty_values: int = 0
    sensitive_count: int = 0

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"CountResult(total={self.total}, empty={self.empty_values}, "
            f"non_empty={self.non_empty_values}, sensitive={self.sensitive_count})"
        )


_SENSITIVE_SUBSTRINGS = ("SECRET", "PASSWORD", "TOKEN", "KEY", "PASSWD", "CREDENTIAL")


def _is_sensitive(key: str) -> bool:
    upper = key.upper()
    return any(s in upper for s in _SENSITIVE_SUBSTRINGS)


def count_keys(
    env: Dict[str, str],
    prefixes: Optional[List[str]] = None,
) -> CountResult:
    """Count keys in *env*, optionally broken down by *prefixes*."""
    total = len(env)
    empty = sum(1 for v in env.values() if v == "")
    non_empty = total - empty
    sensitive = sum(1 for k in env if _is_sensitive(k))

    by_prefix: Dict[str, int] = {}
    if prefixes:
        for prefix in prefixes:
            by_prefix[prefix] = sum(
                1 for k in env if k.upper().startswith(prefix.upper())
            )

    return CountResult(
        total=total,
        by_prefix=by_prefix,
        empty_values=empty,
        non_empty_values=non_empty,
        sensitive_count=sensitive,
    )


def count_summary(result: CountResult) -> str:
    """Return a human-readable summary of a CountResult."""
    lines = [
        f"Total keys    : {result.total}",
        f"Non-empty     : {result.non_empty_values}",
        f"Empty         : {result.empty_values}",
        f"Sensitive     : {result.sensitive_count}",
    ]
    if result.by_prefix:
        lines.append("By prefix:")
        for prefix, cnt in sorted(result.by_prefix.items()):
            lines.append(f"  {prefix}: {cnt}")
    return "\n".join(lines)
