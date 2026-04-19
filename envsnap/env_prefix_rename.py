"""Bulk-rename environment variable keys by replacing a key prefix."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class PrefixRenameResult:
    snapshot: Dict[str, str]
    renamed: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"PrefixRenameResult(renamed={len(self.renamed)}, "
            f"skipped={len(self.skipped)})"
        )


def rename_prefix(
    snapshot: Dict[str, str],
    old_prefix: str,
    new_prefix: str,
    *,
    overwrite: bool = False,
) -> PrefixRenameResult:
    """Return a new snapshot with *old_prefix* replaced by *new_prefix* on matching keys.

    Keys that do not start with *old_prefix* are kept as-is.
    If the resulting new key already exists and *overwrite* is False the key is
    left under its original name and recorded in ``skipped``.
    """
    result: Dict[str, str] = {}
    renamed: List[str] = []
    skipped: List[str] = []

    for key, value in snapshot.items():
        if key.startswith(old_prefix):
            new_key = new_prefix + key[len(old_prefix):]
            if new_key in snapshot and not overwrite:
                # keep original
                result[key] = value
                skipped.append(key)
            else:
                result[new_key] = value
                renamed.append(key)
        else:
            result[key] = value

    return PrefixRenameResult(snapshot=result, renamed=renamed, skipped=skipped)


def prefix_rename_summary(result: PrefixRenameResult) -> str:
    """Return a human-readable summary of a PrefixRenameResult."""
    lines = [f"Renamed : {len(result.renamed)} key(s)"]
    if result.renamed:
        lines += [f"  {k}" for k in sorted(result.renamed)]
    lines.append(f"Skipped : {len(result.skipped)} key(s)")
    if result.skipped:
        lines += [f"  {k}" for k in sorted(result.skipped)]
    return "\n".join(lines)
