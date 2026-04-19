"""Extract a subset of keys from a snapshot into a new snapshot."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ExtractResult:
    env: Dict[str, str]
    extracted: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return (
            f"ExtractResult(extracted={len(self.extracted)}, "
            f"missing={len(self.missing)})"
        )


def extract_keys(
    snap: Dict[str, str],
    keys: List[str],
    *,
    default: Optional[str] = None,
    skip_missing: bool = True,
) -> ExtractResult:
    """Extract specific keys from a snapshot.

    Args:
        snap: Source snapshot dict.
        keys: Keys to extract.
        default: Value to use for missing keys when skip_missing is False.
        skip_missing: If True, missing keys are omitted; otherwise filled with default.

    Returns:
        ExtractResult with the new env and lists of extracted/missing keys.
    """
    env: Dict[str, str] = {}
    extracted: List[str] = []
    missing: List[str] = []

    for key in keys:
        if key in snap:
            env[key] = snap[key]
            extracted.append(key)
        else:
            missing.append(key)
            if not skip_missing:
                env[key] = default if default is not None else ""

    return ExtractResult(env=env, extracted=extracted, missing=missing)


def extract_summary(result: ExtractResult) -> str:
    lines = [f"Extracted {len(result.extracted)} key(s)."]
    if result.missing:
        lines.append(f"Missing ({len(result.missing)}): {', '.join(sorted(result.missing))}")
    return "\n".join(lines)
