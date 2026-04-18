"""Map environment variable keys to human-friendly aliases."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

AliasMap = Dict[str, str]  # alias -> real key


def _alias_path(store_dir: str = ".envsnap") -> Path:
    return Path(store_dir) / "aliases.json"


def load_aliases(store_dir: str = ".envsnap") -> AliasMap:
    path = _alias_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_aliases(aliases: AliasMap, store_dir: str = ".envsnap") -> None:
    path = _alias_path(store_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(aliases, indent=2, sort_keys=True))


def add_alias(alias: str, real_key: str, store_dir: str = ".envsnap") -> AliasMap:
    aliases = load_aliases(store_dir)
    aliases[alias] = real_key
    save_aliases(aliases, store_dir)
    return aliases


def remove_alias(alias: str, store_dir: str = ".envsnap") -> AliasMap:
    aliases = load_aliases(store_dir)
    aliases.pop(alias, None)
    save_aliases(aliases, store_dir)
    return aliases


def resolve(alias: str, aliases: AliasMap) -> str:
    """Return the real key for *alias*, or *alias* itself if not mapped."""
    return aliases.get(alias, alias)


def apply_aliases(env: Dict[str, str], aliases: AliasMap) -> Dict[str, str]:
    """Return a copy of *env* with aliased keys added alongside originals."""
    result = dict(env)
    for alias, real_key in aliases.items():
        if real_key in env:
            result[alias] = env[real_key]
    return result


def reverse_map(aliases: AliasMap) -> Dict[str, list]:
    """Return mapping of real_key -> list of aliases pointing to it."""
    rev: Dict[str, list] = {}
    for alias, real_key in aliases.items():
        rev.setdefault(real_key, []).append(alias)
    return rev
