"""Lock specific env keys to expected values, raising on drift."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class LockViolation:
    key: str
    expected: str
    actual: Optional[str]  # None means key is missing

    def __str__(self) -> str:
        if self.actual is None:
            return f"{self.key}: expected '{self.expected}' but key is missing"
        return f"{self.key}: expected '{self.expected}' but got '{self.actual}'"


def _lock_path(path: str) -> Path:
    return Path(path)


def load_lock(path: str) -> Dict[str, str]:
    p = _lock_path(path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_lock(locked: Dict[str, str], path: str) -> None:
    _lock_path(path).write_text(json.dumps(locked, sort_keys=True, indent=2))


def lock_keys(snapshot: Dict, keys: List[str]) -> Dict[str, str]:
    """Extract key->value pairs from snapshot to form a lock dict."""
    env: Dict[str, str] = snapshot.get("env", {})
    return {k: env[k] for k in keys if k in env}


def check_lock(snapshot: Dict, locked: Dict[str, str]) -> List[LockViolation]:
    """Return violations where snapshot deviates from locked values."""
    env: Dict[str, str] = snapshot.get("env", {})
    violations: List[LockViolation] = []
    for key, expected in locked.items():
        actual = env.get(key)
        if actual != expected:
            violations.append(LockViolation(key=key, expected=expected, actual=actual))
    return violations


def lock_summary(violations: List[LockViolation]) -> str:
    if not violations:
        return "All locked keys match."
    lines = [f"  - {v}" for v in violations]
    return "Lock violations ({}):\n{}".format(len(violations), "\n".join(lines))
