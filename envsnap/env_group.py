"""Group environment variables by prefix or custom mapping."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class EnvGroup:
    name: str
    keys: List[str] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.keys)


def group_by_prefix(
    snapshot: dict,
    prefixes: Optional[List[str]] = None,
    other_label: str = "other",
) -> Dict[str, EnvGroup]:
    """Group snapshot keys by prefix. Keys not matching any prefix go to other_label."""
    env_vars: dict = snapshot.get("vars", {})
    groups: Dict[str, EnvGroup] = {}

    if not prefixes:
        groups[other_label] = EnvGroup(name=other_label, keys=sorted(env_vars.keys()))
        return groups

    assigned: set = set()
    for prefix in prefixes:
        matched = sorted(k for k in env_vars if k.startswith(prefix) and k not in assigned)
        assigned.update(matched)
        groups[prefix] = EnvGroup(name=prefix, keys=matched)

    leftover = sorted(k for k in env_vars if k not in assigned)
    if leftover:
        groups[other_label] = EnvGroup(name=other_label, keys=leftover)

    return groups


def group_by_mapping(
    snapshot: dict,
    mapping: Dict[str, List[str]],
    other_label: str = "other",
) -> Dict[str, EnvGroup]:
    """Group snapshot keys by explicit mapping of group_name -> list of keys."""
    env_vars: dict = snapshot.get("vars", {})
    groups: Dict[str, EnvGroup] = {}
    assigned: set = set()

    for group_name, keys in mapping.items():
        matched = sorted(k for k in keys if k in env_vars)
        assigned.update(matched)
        groups[group_name] = EnvGroup(name=group_name, keys=matched)

    leftover = sorted(k for k in env_vars if k not in assigned)
    if leftover:
        groups[other_label] = EnvGroup(name=other_label, keys=leftover)

    return groups


def group_summary(groups: Dict[str, EnvGroup]) -> str:
    lines = []
    for name, group in groups.items():
        lines.append(f"[{name}] ({len(group)} keys)")
        for k in group.keys:
            lines.append(f"  {k}")
    return "\n".join(lines)
