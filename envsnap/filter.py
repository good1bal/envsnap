"""Filtering utilities for environment variable snapshots."""
from __future__ import annotations

import re
from typing import Dict, List, Optional


def filter_by_prefix(env: Dict[str, str], prefixes: List[str]) -> Dict[str, str]:
    """Return only keys that start with any of the given prefixes."""
    if not prefixes:
        return dict(env)
    return {k: v for k, v in env.items() if any(k.startswith(p) for p in prefixes)}


def exclude_by_prefix(env: Dict[str, str], prefixes: List[str]) -> Dict[str, str]:
    """Return keys that do NOT start with any of the given prefixes."""
    if not prefixes:
        return dict(env)
    return {k: v for k, v in env.items() if not any(k.startswith(p) for p in prefixes)}


def filter_by_pattern(env: Dict[str, str], pattern: str) -> Dict[str, str]:
    """Return only keys matching the given regex pattern."""
    compiled = re.compile(pattern)
    return {k: v for k, v in env.items() if compiled.search(k)}


def mask_values(
    env: Dict[str, str],
    sensitive_prefixes: Optional[List[str]] = None,
    mask: str = "***",
) -> Dict[str, str]:
    """Replace values of sensitive keys with a mask string."""
    if sensitive_prefixes is None:
        sensitive_prefixes = ["SECRET", "PASSWORD", "TOKEN", "API_KEY", "PRIVATE"]
    result = {}
    for k, v in env.items():
        if any(k.upper().startswith(p.upper()) for p in sensitive_prefixes):
            result[k] = mask
        else:
            result[k] = v
    return result


def select_keys(env: Dict[str, str], keys: List[str]) -> Dict[str, str]:
    """Return a subset of the env dict containing only the specified keys."""
    return {k: env[k] for k in keys if k in env}
