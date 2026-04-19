"""Truncate environment variable values to a maximum length."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TruncateResult:
    snapshot: Dict[str, str]
    truncated_keys: List[str] = field(default_factory=list)
    original_lengths: Dict[str, int] = field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f"TruncateResult(truncated={len(self.truncated_keys)}, "
            f"keys={self.truncated_keys})"
        )


def truncate_values(
    snapshot: Dict[str, str],
    max_length: int,
    suffix: str = "...",
    keys: Optional[List[str]] = None,
) -> TruncateResult:
    """Truncate values in *snapshot* that exceed *max_length*.

    Args:
        snapshot: mapping of env var names to values.
        max_length: maximum allowed length (inclusive) for a value.
        suffix: appended to truncated values; counts toward *max_length*.
        keys: if provided, only consider these keys.

    Returns:
        TruncateResult with the modified snapshot and metadata.

    Raises:
        ValueError: if *max_length* is negative or less than ``len(suffix)``.
    """
    if max_length < 0:
        raise ValueError(f"max_length ({max_length}) must be non-negative")
    if max_length < len(suffix):
        raise ValueError(
            f"max_length ({max_length}) must be >= len(suffix) ({len(suffix)})"
        )

    result: Dict[str, str] = {}
    truncated: List[str] = []
    original_lengths: Dict[str, int] = {}

    target_keys = set(keys) if keys is not None else set(snapshot)

    for k, v in snapshot.items():
        if k in target_keys and len(v) > max_length:
            original_lengths[k] = len(v)
            result[k] = v[: max_length - len(suffix)] + suffix
            truncated.append(k)
        else:
            result[k] = v

    return TruncateResult(
        snapshot=result,
        truncated_keys=truncated,
        original_lengths=original_lengths,
    )


def truncate_summary(result: TruncateResult) -> str:
    """Return a human-readable summary of a TruncateResult."""
    if not result.truncated_keys:
        return "No values truncated."
    lines = [f"Truncated {len(result.truncated_keys)} value(s):"]
    for k in result.truncated_keys:
        orig = result.original_lengths[k]
        new_len = len(result.snapshot[k])
        lines.append(f"  {k}: {orig} -> {new_len} chars")
    return "\n".join(lines)
