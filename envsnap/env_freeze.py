"""Freeze a snapshot so its keys cannot be modified without explicit unfreeze."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class FreezeViolation:
    key: str
    reason: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"FreezeViolation(key={self.key!r}, reason={self.reason!r})"


@dataclass
class FreezeResult:
    frozen_keys: List[str] = field(default_factory=list)
    skipped_keys: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"FreezeResult(frozen={len(self.frozen_keys)}, "
            f"skipped={len(self.skipped_keys)})"
        )


def _freeze_path(store_dir: str = ".envsnap") -> Path:
    return Path(store_dir) / "frozen.json"


def load_frozen(store_dir: str = ".envsnap") -> Dict[str, str]:
    """Return mapping of frozen key -> locked value."""
    path = _freeze_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_frozen(frozen: Dict[str, str], store_dir: str = ".envsnap") -> None:
    path = _freeze_path(store_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(frozen, sort_keys=True, indent=2))


def freeze_keys(
    snapshot: Dict[str, str],
    keys: Optional[List[str]] = None,
    store_dir: str = ".envsnap",
) -> FreezeResult:
    """Freeze *keys* (or all keys) from *snapshot*."""
    frozen = load_frozen(store_dir)
    result = FreezeResult()
    targets = keys if keys is not None else list(snapshot.get("env", snapshot).keys())
    env = snapshot.get("env", snapshot)
    for key in targets:
        if key in env:
            frozen[key] = env[key]
            result.frozen_keys.append(key)
        else:
            result.skipped_keys.append(key)
    save_frozen(frozen, store_dir)
    return result


def unfreeze_keys(
    keys: List[str],
    store_dir: str = ".envsnap",
) -> List[str]:
    """Remove *keys* from the freeze store. Returns list of keys actually removed."""
    frozen = load_frozen(store_dir)
    removed = [k for k in keys if k in frozen]
    for k in removed:
        del frozen[k]
    save_frozen(frozen, store_dir)
    return removed


def check_freeze(
    snapshot: Dict[str, str],
    store_dir: str = ".envsnap",
) -> List[FreezeViolation]:
    """Return violations where snapshot values differ from frozen values."""
    frozen = load_frozen(store_dir)
    env = snapshot.get("env", snapshot)
    violations: List[FreezeViolation] = []
    for key, locked_value in frozen.items():
        if key not in env:
            violations.append(FreezeViolation(key=key, reason="key missing from snapshot"))
        elif env[key] != locked_value:
            violations.append(FreezeViolation(key=key, reason="value changed from frozen"))
    return violations


def freeze_summary(result: FreezeResult) -> str:
    lines = [f"Frozen : {len(result.frozen_keys)}"]
    if result.skipped_keys:
        lines.append(f"Skipped: {len(result.skipped_keys)} (key not in snapshot)")
    return "\n".join(lines)
