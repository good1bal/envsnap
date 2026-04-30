"""env_protect.py — mark keys as protected and prevent accidental mutation."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ProtectViolation:
    key: str
    reason: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"ProtectViolation(key={self.key!r}, reason={self.reason!r})"


@dataclass
class ProtectResult:
    env: Dict[str, str]
    protected: List[str] = field(default_factory=list)
    violations: List[ProtectViolation] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"ProtectResult(protected={len(self.protected)}, "
            f"violations={len(self.violations)})"
        )


def _protect_path(store: Optional[Path] = None) -> Path:
    base = store or Path(".envsnap")
    base.mkdir(parents=True, exist_ok=True)
    return base / "protected.json"


def load_protected(store: Optional[Path] = None) -> List[str]:
    path = _protect_path(store)
    if not path.exists():
        return []
    return json.loads(path.read_text())


def save_protected(keys: List[str], store: Optional[Path] = None) -> None:
    path = _protect_path(store)
    path.write_text(json.dumps(sorted(set(keys)), indent=2))


def protect_keys(
    env: Dict[str, str],
    keys: List[str],
    store: Optional[Path] = None,
) -> ProtectResult:
    """Add *keys* to the protected set and return current env unchanged."""
    existing = load_protected(store)
    merged = sorted(set(existing) | set(keys))
    save_protected(merged, store)
    registered = [k for k in keys if k in env]
    return ProtectResult(env=dict(env), protected=registered)


def check_protected(
    original: Dict[str, str],
    updated: Dict[str, str],
    store: Optional[Path] = None,
) -> ProtectResult:
    """Check *updated* against *original* for mutations to protected keys."""
    protected = load_protected(store)
    violations: List[ProtectViolation] = []
    for key in protected:
        if key in original and key not in updated:
            violations.append(ProtectViolation(key=key, reason="deleted"))
        elif key in original and updated.get(key) != original[key]:
            violations.append(ProtectViolation(key=key, reason="modified"))
    return ProtectResult(env=dict(updated), protected=protected, violations=violations)


def protect_summary(result: ProtectResult) -> str:
    lines = [f"Protected keys : {len(result.protected)}"]
    if result.violations:
        lines.append(f"Violations     : {len(result.violations)}")
        for v in result.violations:
            lines.append(f"  [{v.reason}] {v.key}")
    else:
        lines.append("Violations     : 0")
    return "\n".join(lines)
