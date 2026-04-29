"""Redaction helpers — strip or mask sensitive data before saving/exporting."""
from __future__ import annotations

from typing import Dict, List, Tuple

DEFAULT_SENSITIVE_SUBSTRINGS: List[str] = [
    "DATABASE_URL",
    "SECRET",
    "PASSWORD",
    "PASSWD",
    "TOKEN",
    "API_KEY",
    "PRIVATE",
    "CREDENTIAL",
    "AUTH",
]


def is_sensitive(key: str, substrings: List[str] = DEFAULT_SENSITIVE_SUBSTRINGS) -> bool:
    """Return True if *key* contains any of the sensitive substrings (case-insensitive)."""
    upper = key.upper()
    return any(s in upper for s in substrings)


def redact(
    env: Dict[str, str],
    substrings: List[str] = DEFAULT_SENSITIVE_SUBSTRINGS,
    placeholder: str = "<redacted>",
) -> Dict[str, str]:
    """Return a copy of *env* with sensitive values replaced by *placeholder*."""
    return {
        k: (placeholder if is_sensitive(k, substrings) else v)
        for k, v in env.items()
    }


def split_sensitive(
    env: Dict[str, str],
    substrings: List[str] = DEFAULT_SENSITIVE_SUBSTRINGS,
) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Split *env* into (safe, sensitive) dicts.

    Returns:
        safe      – variables whose keys are NOT sensitive
        sensitive – variables whose keys ARE sensitive
    """
    safe: Dict[str, str] = {}
    sensitive: Dict[str, str] = {}
    for k, v in env.items():
        if is_sensitive(k, substrings):
            sensitive[k] = v
        else:
            safe[k] = v
    return safe, sensitive
