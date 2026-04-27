"""Classify environment variables into semantic categories."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

# Default category patterns (key substring → category)
_DEFAULT_RULES: List[tuple[str, str]] = [
    ("SECRET", "secrets"),
    ("PASSWORD", "secrets"),
    ("PASSWD", "secrets"),
    ("TOKEN", "secrets"),
    ("API_KEY", "secrets"),
    ("DATABASE", "database"),
    ("DB_", "database"),
    ("REDIS", "database"),
    ("MONGO", "database"),
    ("HOST", "networking"),
    ("PORT", "networking"),
    ("URL", "networking"),
    ("ADDR", "networking"),
    ("LOG", "logging"),
    ("DEBUG", "logging"),
    ("VERBOSE", "logging"),
    ("PATH", "filesystem"),
    ("DIR", "filesystem"),
    ("FILE", "filesystem"),
]

OTHER = "other"


@dataclass
class ClassifyResult:
    categories: Dict[str, List[str]] = field(default_factory=dict)
    key_map: Dict[str, str] = field(default_factory=dict)

    def __repr__(self) -> str:
        cats = ", ".join(f"{k}:{len(v)}" for k, v in sorted(self.categories.items()))
        return f"ClassifyResult({cats})"


def classify(
    env: Dict[str, str],
    rules: Optional[List[tuple[str, str]]] = None,
    key_fn: Optional[Callable[[str], str]] = None,
) -> ClassifyResult:
    """Classify keys in *env* into named categories.

    Rules are evaluated in order; the first match wins.
    Keys that match no rule are placed in ``other``.
    """
    active_rules = rules if rules is not None else _DEFAULT_RULES
    transform = key_fn or (lambda k: k.upper())

    categories: Dict[str, List[str]] = {}
    key_map: Dict[str, str] = {}

    for key in env:
        normalised = transform(key)
        matched = OTHER
        for pattern, category in active_rules:
            if pattern.upper() in normalised:
                matched = category
                break
        categories.setdefault(matched, []).append(key)
        key_map[key] = matched

    return ClassifyResult(categories=categories, key_map=key_map)


def classify_summary(result: ClassifyResult) -> str:
    """Return a human-readable summary of classification results."""
    lines = ["Classification summary:"]
    for cat, keys in sorted(result.categories.items()):
        lines.append(f"  {cat}: {len(keys)} key(s)")
    return "\n".join(lines)
