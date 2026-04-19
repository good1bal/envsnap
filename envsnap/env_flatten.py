"""Flatten nested env-like structures into a single-level snapshot."""
from __future__ import annotations
from typing import Any


class FlattenError(Exception):
    pass


def flatten(data: dict[str, Any], separator: str = "__", prefix: str = "") -> dict[str, str]:
    """Recursively flatten a nested dict into a flat key=value mapping."""
    result: dict[str, str] = {}
    for key, value in data.items():
        full_key = f"{prefix}{separator}{key}" if prefix else key
        if not isinstance(key, str):
            raise FlattenError(f"Non-string key encountered: {key!r}")
        if isinstance(value, dict):
            nested = flatten(value, separator=separator, prefix=full_key)
            result.update(nested)
        elif isinstance(value, (list, tuple)):
            for i, item in enumerate(value):
                indexed_key = f"{full_key}{separator}{i}"
                if isinstance(item, dict):
                    result.update(flatten(item, separator=separator, prefix=indexed_key))
                else:
                    result[indexed_key] = str(item)
        else:
            result[full_key] = str(value) if value is not None else ""
    return result


def unflatten(data: dict[str, str], separator: str = "__") -> dict[str, Any]:
    """Reconstruct a nested dict from a flat key=value mapping."""
    result: dict[str, Any] = {}
    for flat_key, value in data.items():
        parts = flat_key.split(separator)
        node = result
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = value
    return result


def flatten_summary(original: dict[str, Any], flat: dict[str, str]) -> str:
    """Return a short summary of the flatten operation."""
    return (
        f"Flattened {len(original)} top-level key(s) "
        f"into {len(flat)} flat key(s)."
    )
