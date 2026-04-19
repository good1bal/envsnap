"""Mask environment variable values based on rules."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional

DEFAULT_MASK = "***"
_SENSITIVE_SUBSTRINGS = ("SECRET", "PASSWORD", "TOKEN", "KEY", "PASSWD", "CREDENTIAL")


@dataclass
class MaskResult:
    original: Dict[str, str]
    masked: Dict[str, str]
    mask_keys: List[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"MaskResult(masked={len(self.mask_keys)} keys)"


def _is_sensitive(key: str, sensitive_substrings: tuple) -> bool:
    upper = key.upper()
    return any(s in upper for s in sensitive_substrings)


def mask_snapshot(
    snap: Dict[str, str],
    keys: Optional[List[str]] = None,
    placeholder: str = DEFAULT_MASK,
    sensitive_substrings: tuple = _SENSITIVE_SUBSTRINGS,
    auto_detect: bool = True,
) -> MaskResult:
    """Return a copy of snap with sensitive values replaced by placeholder."""
    to_mask = set(keys or [])
    if auto_detect:
        for k in snap:
            if _is_sensitive(k, sensitive_substrings):
                to_mask.add(k)
    masked = {k: (placeholder if k in to_mask else v) for k, v in snap.items()}
    return MaskResult(original=snap, masked=masked, mask_keys=sorted(to_mask & snap.keys()))


def mask_summary(result: MaskResult) -> str:
    if not result.mask_keys:
        return "No keys masked."
    lines = [f"Masked {len(result.mask_keys)} key(s):"]
    for k in result.mask_keys:
        lines.append(f"  {k}")
    return "\n".join(lines)
