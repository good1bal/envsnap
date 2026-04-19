"""Cast environment variable string values to typed Python values."""

from __future__ import annotations

from typing import Any

_BOOL_TRUE = {"1", "true", "yes", "on"}
_BOOL_FALSE = {"0", "false", "no", "off"}


class CastError(ValueError):
    """Raised when a value cannot be cast to the requested type."""


def cast_bool(value: str) -> bool:
    v = value.strip().lower()
    if v in _BOOL_TRUE:
        return True
    if v in _BOOL_FALSE:
        return False
    raise CastError(f"Cannot cast {value!r} to bool")


def cast_int(value: str) -> int:
    try:
        return int(value.strip())
    except ValueError:
        raise CastError(f"Cannot cast {value!r} to int")


def cast_float(value: str) -> float:
    try:
        return float(value.strip())
    except ValueError:
        raise CastError(f"Cannot cast {value!r} to float")


def cast_list(value: str, sep: str = ",") -> list[str]:
    return [item.strip() for item in value.split(sep) if item.strip()]


_CASTERS = {
    "bool": cast_bool,
    "int": cast_int,
    "float": cast_float,
    "list": cast_list,
    "str": str,
}


def cast(value: str, type_name: str, **kwargs: Any) -> Any:
    """Cast *value* to *type_name*. Extra kwargs forwarded to the caster."""
    if type_name not in _CASTERS:
        raise CastError(f"Unknown type {type_name!r}. Choose from {list(_CASTERS)}")
    return _CASTERS[type_name](value, **kwargs)


def cast_snapshot(env: dict[str, str], schema: dict[str, str]) -> dict[str, Any]:
    """Apply per-key type casts defined in *schema* to *env*.

    Keys absent from *schema* are returned as plain strings.
    """
    result: dict[str, Any] = {}
    for key, value in env.items():
        type_name = schema.get(key, "str")
        result[key] = cast(value, type_name)
    return result
