"""Check and enforce required environment variable keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RequiredCheckResult:
    present: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)
    defaults_applied: Dict[str, str] = field(default_factory=dict)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"RequiredCheckResult(present={len(self.present)}, "
            f"missing={len(self.missing)}, "
            f"defaults_applied={len(self.defaults_applied)})"
        )

    @property
    def satisfied(self) -> bool:
        return len(self.missing) == 0


def check_required(
    snap: Dict[str, str],
    required: List[str],
    defaults: Optional[Dict[str, str]] = None,
    apply_defaults: bool = False,
) -> RequiredCheckResult:
    """Check which required keys are present or missing in *snap*.

    If *apply_defaults* is True and a default value is available for a missing
    key, the key is considered satisfied and recorded in *defaults_applied*.
    """
    defaults = defaults or {}
    result = RequiredCheckResult()
    env = dict(snap)

    for key in required:
        if key in env:
            result.present.append(key)
        elif apply_defaults and key in defaults:
            env[key] = defaults[key]
            result.defaults_applied[key] = defaults[key]
            result.present.append(key)
        else:
            result.missing.append(key)

    return result


def required_summary(result: RequiredCheckResult) -> str:
    """Return a human-readable summary of a RequiredCheckResult."""
    lines = [
        f"Required keys : {len(result.present) + len(result.missing)}",
        f"  Present     : {len(result.present)}",
        f"  Missing     : {len(result.missing)}",
    ]
    if result.defaults_applied:
        lines.append(f"  Defaulted   : {len(result.defaults_applied)}")
        for k, v in sorted(result.defaults_applied.items()):
            lines.append(f"    {k} = {v}")
    if result.missing:
        lines.append("Missing keys:")
        for k in sorted(result.missing):
            lines.append(f"  - {k}")
    return "\n".join(lines)
