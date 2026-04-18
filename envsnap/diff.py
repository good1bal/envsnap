"""Diff two environment snapshots and report changes."""

from typing import TypedDict


class DiffResult(TypedDict):
    added: dict
    removed: dict
    changed: dict
    unchanged: dict


def compare(before: dict, after: dict) -> DiffResult:
    """Return a structured diff between two snapshot dicts."""
    env_before: dict = before.get("env", {})
    env_after: dict = after.get("env", {})

    keys_before = set(env_before)
    keys_after = set(env_after)

    added = {k: env_after[k] for k in keys_after - keys_before}
    removed = {k: env_before[k] for k in keys_before - keys_after}
    changed = {
        k: {"before": env_before[k], "after": env_after[k]}
        for k in keys_before & keys_after
        if env_before[k] != env_after[k]
    }
    unchanged = {
        k: env_before[k]
        for k in keys_before & keys_after
        if env_before[k] == env_after[k]
    }

    return DiffResult(added=added, removed=removed, changed=changed, unchanged=unchanged)


def summary(diff: DiffResult) -> str:
    """Return a human-readable summary string of a diff result."""
    lines = [
        f"+ Added   : {len(diff['added'])}",
        f"- Removed : {len(diff['removed'])}",
        f"~ Changed : {len(diff['changed'])}",
        f"= Unchanged: {len(diff['unchanged'])}",
    ]
    return "\n".join(lines)
