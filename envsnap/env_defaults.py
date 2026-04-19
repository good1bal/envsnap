"""Apply and manage default values for missing environment keys."""
from __future__ import annotations
from typing import Any


class DefaultApplyResult:
    def __init__(self, snapshot: dict, applied: dict[str, str], skipped: list[str]):
        self.snapshot = snapshot
        self.applied = applied
        self.skipped = skipped

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"DefaultApplyResult(applied={list(self.applied)}, "
            f"skipped={self.skipped})"
        )


def apply_defaults(
    snapshot: dict,
    defaults: dict[str, str],
    *,
    overwrite: bool = False,
) -> DefaultApplyResult:
    """Apply *defaults* to *snapshot*, returning a new snapshot dict.

    Args:
        snapshot: Existing snapshot (as returned by ``capture``/``load``).
        defaults: Mapping of key -> default value.
        overwrite: If True, set the default even when the key already exists.

    Returns:
        A :class:`DefaultApplyResult` with the merged snapshot, which keys
        were actually applied, and which were skipped (already present).
    """
    env: dict[str, Any] = dict(snapshot)
    applied: dict[str, str] = {}
    skipped: list[str] = []

    for key, value in defaults.items():
        if key not in env.get("env", {}) or overwrite:
            env.setdefault("env", {})[key] = value
            applied[key] = value
        else:
            skipped.append(key)

    return DefaultApplyResult(snapshot=env, applied=applied, skipped=skipped)


def missing_keys(snapshot: dict, defaults: dict[str, str]) -> list[str]:
    """Return keys in *defaults* that are absent from *snapshot*."""
    env_vars: dict = snapshot.get("env", {})
    return [k for k in defaults if k not in env_vars]


def defaults_summary(result: DefaultApplyResult) -> str:
    """Human-readable summary of a :class:`DefaultApplyResult`."""
    lines = []
    if result.applied:
        lines.append(f"Applied {len(result.applied)} default(s):")
        for k, v in result.applied.items():
            lines.append(f"  + {k}={v}")
    if result.skipped:
        lines.append(f"Skipped {len(result.skipped)} key(s) (already set):")
        for k in result.skipped:
            lines.append(f"  ~ {k}")
    if not lines:
        lines.append("No defaults applied.")
    return "\n".join(lines)
