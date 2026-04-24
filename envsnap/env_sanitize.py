"""Sanitize environment variable keys and values.

Provides utilities to strip invalid characters from keys, enforce naming
conventions, and clean up values (e.g. remove null bytes, control chars).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

_VALID_KEY_RE = re.compile(r"[^A-Z0-9_]")
_CONTROL_CHAR_RE = re.compile(r"[\x00-\x1f\x7f]")


@dataclass
class SanitizeResult:
    env: Dict[str, str]
    renamed_keys: Dict[str, str] = field(default_factory=dict)   # old -> new
    dropped_keys: List[str] = field(default_factory=list)
    cleaned_values: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"SanitizeResult(keys={len(self.env)}, "
            f"renamed={len(self.renamed_keys)}, "
            f"dropped={len(self.dropped_keys)}, "
            f"cleaned_values={len(self.cleaned_values)})"
        )


def _default_key_fn(key: str) -> Optional[str]:
    """Uppercase and replace invalid chars with underscores. Return None to drop."""
    sanitized = _VALID_KEY_RE.sub("_", key.upper())
    # A key that becomes all underscores is considered invalid
    if not sanitized or sanitized.replace("_", "") == "":
        return None
    return sanitized


def sanitize_keys(
    snap: Dict[str, str],
    key_fn: Callable[[str], Optional[str]] = _default_key_fn,
) -> SanitizeResult:
    """Apply *key_fn* to every key.  Duplicate results keep the last writer."""
    env: Dict[str, str] = {}
    renamed: Dict[str, str] = {}
    dropped: List[str] = []

    for k, v in snap.items():
        new_k = key_fn(k)
        if new_k is None:
            dropped.append(k)
        else:
            env[new_k] = v
            if new_k != k:
                renamed[k] = new_k

    return SanitizeResult(env=env, renamed_keys=renamed, dropped_keys=dropped)


def sanitize_values(
    snap: Dict[str, str],
    value_fn: Optional[Callable[[str], str]] = None,
) -> SanitizeResult:
    """Strip control characters from values (or apply a custom *value_fn*)."""
    if value_fn is None:
        value_fn = lambda v: _CONTROL_CHAR_RE.sub("", v)

    env: Dict[str, str] = {}
    cleaned: List[str] = []

    for k, v in snap.items():
        new_v = value_fn(v)
        env[k] = new_v
        if new_v != v:
            cleaned.append(k)

    return SanitizeResult(env=env, cleaned_values=cleaned)


def sanitize_summary(result: SanitizeResult) -> str:
    parts: List[str] = [f"{len(result.env)} keys"]
    if result.renamed_keys:
        parts.append(f"{len(result.renamed_keys)} renamed")
    if result.dropped_keys:
        parts.append(f"{len(result.dropped_keys)} dropped")
    if result.cleaned_values:
        parts.append(f"{len(result.cleaned_values)} values cleaned")
    return ", ".join(parts)
