"""Scope support: tag snapshot keys with a named scope and filter by scope."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SCOPE_KEY = "__scopes__"


@dataclass
class ScopeMap:
    mapping: Dict[str, str] = field(default_factory=dict)  # key -> scope

    def __len__(self) -> int:
        return len(self.mapping)


def assign_scope(snapshot: dict, keys: List[str], scope: str) -> dict:
    """Return a new snapshot with __scopes__ updated to assign *scope* to each key."""
    snap = dict(snapshot)
    scopes: Dict[str, str] = dict(snap.get(SCOPE_KEY) or {})
    for k in keys:
        if k in snap:
            scopes[k] = scope
    snap[SCOPE_KEY] = scopes
    return snap


def filter_by_scope(snapshot: dict, scope: str) -> dict:
    """Return env vars whose assigned scope matches *scope*."""
    scopes: Dict[str, str] = snapshot.get(SCOPE_KEY) or {}
    env = snapshot.get("env", snapshot)
    if "env" in snapshot:
        return {k: v for k, v in snapshot["env"].items() if scopes.get(k) == scope}
    return {k: v for k, v in snapshot.items() if k != SCOPE_KEY and scopes.get(k) == scope}


def get_scope(snapshot: dict, key: str) -> Optional[str]:
    """Return the scope assigned to *key*, or None."""
    scopes: Dict[str, str] = snapshot.get(SCOPE_KEY) or {}
    return scopes.get(key)


def scope_summary(snapshot: dict) -> Dict[str, List[str]]:
    """Return a dict mapping each scope name to its list of keys."""
    scopes: Dict[str, str] = snapshot.get(SCOPE_KEY) or {}
    result: Dict[str, List[str]] = {}
    for k, s in scopes.items():
        result.setdefault(s, []).append(k)
    return result


def remove_scope(snapshot: dict, key: str) -> dict:
    """Return a new snapshot with the scope assignment for *key* removed."""
    snap = dict(snapshot)
    scopes = dict(snap.get(SCOPE_KEY) or {})
    scopes.pop(key, None)
    snap[SCOPE_KEY] = scopes
    return snap
