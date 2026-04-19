"""Copy and clone snapshot keys with optional transformations."""
from __future__ import annotations
from typing import Dict, List, Optional
from envsnap.snapshot import capture


class CopyConflict(Exception):
    def __init__(self, key: str):
        super().__init__(f"Key already exists in destination: {key!r}")
        self.key = key


def copy_key(
    snapshot: Dict,
    src: str,
    dst: str,
    overwrite: bool = False,
) -> Dict:
    """Copy a single key within a snapshot, returning a new snapshot."""
    if src not in snapshot["env"]:
        raise KeyError(f"Source key not found: {src!r}")
    if dst in snapshot["env"] and not overwrite:
        raise CopyConflict(dst)
    env = dict(snapshot["env"])
    env[dst] = env[src]
    return {**snapshot, "env": env}


def copy_keys(
    snapshot: Dict,
    mapping: Dict[str, str],
    overwrite: bool = False,
) -> Dict:
    """Copy multiple keys using a src->dst mapping."""
    env = dict(snapshot["env"])
    for src, dst in mapping.items():
        if src not in env:
            raise KeyError(f"Source key not found: {src!r}")
        if dst in env and not overwrite:
            raise CopyConflict(dst)
        env[dst] = env[src]
    return {**snapshot, "env": env}


def clone_snapshot(
    snapshot: Dict,
    label: Optional[str] = None,
    prefix_strip: Optional[str] = None,
    prefix_add: Optional[str] = None,
) -> Dict:
    """Clone a snapshot with optional label and key prefix transformations."""
    env = {}
    for k, v in snapshot["env"].items():
        new_k = k
        if prefix_strip and new_k.startswith(prefix_strip):
            new_k = new_k[len(prefix_strip):]
        if prefix_add:
            new_k = prefix_add + new_k
        env[new_k] = v
    return {
        **snapshot,
        "label": label if label is not None else snapshot.get("label", ""),
        "env": env,
    }


def copy_summary(original: Dict, result: Dict) -> str:
    orig_keys = set(original["env"])
    new_keys = set(result["env"]) - orig_keys
    return f"Copied {len(new_keys)} key(s): {', '.join(sorted(new_keys)) or 'none'}"
