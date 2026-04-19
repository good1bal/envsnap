"""Detect and resolve placeholder values in environment snapshots."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

DEFAULT_PATTERNS = [
    r"^<.+>$",
    r"^\$\{.+\}$",
    r"^CHANGEME$",
    r"^TODO$",
    r"^REPLACE_ME$",
    r"^your[_-].+here$",
]


@dataclass
class PlaceholderResult:
    snapshot: Dict[str, str]
    placeholders: List[str] = field(default_factory=list)
    resolved: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return (
            f"PlaceholderResult(placeholders={len(self.placeholders)}, "
            f"resolved={len(self.resolved)}, skipped={len(self.skipped)})"
        )


def is_placeholder(value: str, patterns: Optional[List[str]] = None) -> bool:
    """Return True if value matches any placeholder pattern."""
    for pat in (patterns or DEFAULT_PATTERNS):
        if re.fullmatch(pat, value, re.IGNORECASE):
            return True
    return False


def find_placeholders(
    snapshot: Dict[str, str],
    patterns: Optional[List[str]] = None,
) -> List[str]:
    """Return keys whose values are placeholders."""
    return [k for k, v in snapshot.items() if is_placeholder(v, patterns)]


def resolve_placeholders(
    snapshot: Dict[str, str],
    overrides: Dict[str, str],
    patterns: Optional[List[str]] = None,
) -> PlaceholderResult:
    """Replace placeholder values using overrides dict."""
    result = dict(snapshot)
    placeholders = find_placeholders(snapshot, patterns)
    resolved: List[str] = []
    skipped: List[str] = []

    for key in placeholders:
        if key in overrides:
            result[key] = overrides[key]
            resolved.append(key)
        else:
            skipped.append(key)

    return PlaceholderResult(
        snapshot=result,
        placeholders=placeholders,
        resolved=resolved,
        skipped=skipped,
    )


def placeholder_summary(result: PlaceholderResult) -> str:
    lines = [f"Placeholders found : {len(result.placeholders)}"]
    if result.resolved:
        lines.append("Resolved : " + ", ".join(result.resolved))
    if result.skipped:
        lines.append("Unresolved: " + ", ".join(result.skipped))
    return "\n".join(lines)
