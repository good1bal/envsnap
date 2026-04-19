"""Split a snapshot into multiple snapshots by prefix or key list."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envsnap.snapshot import capture


@dataclass
class SplitResult:
    parts: Dict[str, dict]
    remainder: dict
    source_label: str

    def __repr__(self) -> str:
        parts = ", ".join(f"{k}({len(v)}keys)" for k, v in self.parts.items())
        return f"SplitResult(parts=[{parts}], remainder={len(self.remainder)}keys)"


def split_by_prefix(
    env: dict,
    prefixes: List[str],
    strip_prefix: bool = False,
    label: str = "snapshot",
) -> SplitResult:
    parts: Dict[str, dict] = {}
    assigned: set = set()
    for prefix in prefixes:
        bucket = {}
        for k, v in env.items():
            if k.startswith(prefix):
                out_key = k[len(prefix):] if strip_prefix else k
                bucket[out_key] = v
                assigned.add(k)
        parts[prefix] = bucket
    remainder = {k: v for k, v in env.items() if k not in assigned}
    return SplitResult(parts=parts, remainder=remainder, source_label=label)


def split_by_keys(
    env: dict,
    groups: Dict[str, List[str]],
    label: str = "snapshot",
) -> SplitResult:
    parts: Dict[str, dict] = {}
    assigned: set = set()
    for group_name, keys in groups.items():
        bucket = {k: env[k] for k in keys if k in env}
        parts[group_name] = bucket
        assigned.update(bucket.keys())
    remainder = {k: v for k, v in env.items() if k not in assigned}
    return SplitResult(parts=parts, remainder=remainder, source_label=label)


def split_summary(result: SplitResult) -> str:
    lines = [f"Source: {result.source_label}"]
    for name, part in result.parts.items():
        lines.append(f"  {name}: {len(part)} key(s)")
    lines.append(f"  (remainder): {len(result.remainder)} key(s)")
    return "\n".join(lines)
