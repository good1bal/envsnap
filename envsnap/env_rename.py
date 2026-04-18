"""Rename keys in a snapshot, with optional conflict handling."""

from __future__ import annotations

from typing import Dict


class RenameConflict(Exception):
    """Raised when a rename target key already exists in the snapshot."""


def rename_key(
    snapshot: Dict,
    old_key: str,
    new_key: str,
    overwrite: bool = False,
) -> Dict:
    """Return a new snapshot with *old_key* renamed to *new_key*.

    Parameters
    ----------
    snapshot:  source snapshot dict (must contain an ``"env"`` sub-dict).
    old_key:   key to rename.
    new_key:   desired new key name.
    overwrite: if *True*, silently replace an existing *new_key*;
               otherwise raise :class:`RenameConflict`.
    """
    if old_key not in snapshot["env"]:
        raise KeyError(f"Key {old_key!r} not found in snapshot.")
    if new_key in snapshot["env"] and not overwrite:
        raise RenameConflict(
            f"Target key {new_key!r} already exists. Use overwrite=True to replace it."
        )
    new_env = {k: v for k, v in snapshot["env"].items() if k != old_key}
    new_env[new_key] = snapshot["env"][old_key]
    return {**snapshot, "env": new_env}


def rename_keys(
    snapshot: Dict,
    mapping: Dict[str, str],
    overwrite: bool = False,
) -> Dict:
    """Apply multiple renames described by *mapping* ``{old: new}``.

    Renames are applied sequentially; the output of each step feeds the next.
    """
    result = snapshot
    for old_key, new_key in mapping.items():
        result = rename_key(result, old_key, new_key, overwrite=overwrite)
    return result


def rename_summary(mapping: Dict[str, str]) -> str:
    """Return a human-readable summary of a rename mapping."""
    if not mapping:
        return "No renames."
    lines = [f"  {old} -> {new}" for old, new in mapping.items()]
    return "Renames:\n" + "\n".join(lines)
