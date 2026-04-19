"""Promote a snapshot from one environment label to another."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envsnap.snapshot import capture


@dataclass
class PromoteResult:
    source_label: str
    target_label: str
    promoted: Dict[str, str]
    skipped: List[str] = field(default_factory=list)
    overwritten: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"PromoteResult(source={self.source_label!r}, target={self.target_label!r}, "
            f"promoted={len(self.promoted)}, skipped={len(self.skipped)}, "
            f"overwritten={len(self.overwritten)})"
        )


def promote(
    source: Dict[str, str],
    target: Dict[str, str],
    source_label: str,
    target_label: str,
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> PromoteResult:
    """Copy selected keys from *source* snapshot into *target* snapshot.

    Args:
        source: Snapshot dict to promote values from.
        target: Snapshot dict to promote values into (not mutated).
        source_label: Human-readable label for the source environment.
        target_label: Human-readable label for the target environment.
        keys: Explicit list of keys to promote; defaults to all keys in source.
        overwrite: When True, overwrite keys that already exist in target.

    Returns:
        PromoteResult with the merged snapshot and metadata.
    """
    candidates = keys if keys is not None else list(source.get("env", source).keys())

    src_env: Dict[str, str] = source.get("env", source)  # type: ignore[arg-type]
    tgt_env: Dict[str, str] = dict(target.get("env", target))  # type: ignore[arg-type]

    promoted: Dict[str, str] = {}
    skipped: List[str] = []
    overwritten: List[str] = []

    for key in candidates:
        if key not in src_env:
            skipped.append(key)
            continue
        if key in tgt_env and not overwrite:
            skipped.append(key)
            continue
        if key in tgt_env:
            overwritten.append(key)
        tgt_env[key] = src_env[key]
        promoted[key] = src_env[key]

    return PromoteResult(
        source_label=source_label,
        target_label=target_label,
        promoted=tgt_env,
        skipped=skipped,
        overwritten=overwritten,
    )


def promote_summary(result: PromoteResult) -> str:
    """Return a human-readable summary of a PromoteResult."""
    lines = [
        f"Promote: {result.source_label} -> {result.target_label}",
        f"  Keys promoted : {len(result.promoted)}",
        f"  Keys skipped  : {len(result.skipped)}",
        f"  Keys overwritten: {len(result.overwritten)}",
    ]
    if result.skipped:
        lines.append("  Skipped: " + ", ".join(sorted(result.skipped)))
    if result.overwritten:
        lines.append("  Overwritten: " + ", ".join(sorted(result.overwritten)))
    return "\n".join(lines)
