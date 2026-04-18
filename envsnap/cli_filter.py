"""CLI helpers that wire filter + redact options into snapshot capture."""
from __future__ import annotations

from typing import Dict, List, Optional

from envsnap.filter import (
    exclude_by_prefix,
    filter_by_pattern,
    filter_by_prefix,
    mask_values,
)
from envsnap.redact import redact


def apply_filters(
    env: Dict[str, str],
    *,
    include_prefixes: Optional[List[str]] = None,
    exclude_prefixes: Optional[List[str]] = None,
    pattern: Optional[str] = None,
    redact_sensitive: bool = False,
    mask_sensitive: bool = False,
    mask_char: str = "***",
) -> Dict[str, str]:
    """Apply a chain of filters/redactions to *env* and return the result.

    Order of operations:
    1. include_prefixes  – keep only matching keys
    2. exclude_prefixes  – drop matching keys
    3. pattern           – keep only keys matching regex
    4. redact_sensitive  – replace sensitive values with ``<redacted>``
    5. mask_sensitive    – replace sensitive values with *mask_char*
    """
    result = dict(env)

    if include_prefixes:
        result = filter_by_prefix(result, include_prefixes)

    if exclude_prefixes:
        result = exclude_by_prefix(result, exclude_prefixes)

    if pattern:
        result = filter_by_pattern(result, pattern)

    if redact_sensitive:
        result = redact(result)

    if mask_sensitive:
        result = mask_values(result, mask=mask_char)

    return result


def build_filter_summary(
    original: Dict[str, str],
    filtered: Dict[str, str],
) -> str:
    """Return a human-readable summary of how many keys were kept/dropped."""
    kept = len(filtered)
    dropped = len(original) - kept
    return f"Keys: {kept} kept, {dropped} dropped (of {len(original)} total)"
