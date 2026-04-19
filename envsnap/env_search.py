"""Search and query environment variables across snapshots."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envsnap.snapshot import load


@dataclass
class SearchResult:
    label: str
    key: str
    value: str

    def __repr__(self) -> str:
        return f"SearchResult(label={self.label!r}, key={self.key!r}, value={self.value!r})"


def search_by_key(
    snapshots: List[Dict],
    pattern: str,
    *,
    case_sensitive: bool = False,
) -> List[SearchResult]:
    """Return all entries whose key matches *pattern* (regex)."""
    flags = 0 if case_sensitive else re.IGNORECASE
    rx = re.compile(pattern, flags)
    results: List[SearchResult] = []
    for snap in snapshots:
        label = snap.get("label", "")
        for key, value in snap.get("env", {}).items():
            if rx.search(key):
                results.append(SearchResult(label=label, key=key, value=value))
    return results


def search_by_value(
    snapshots: List[Dict],
    pattern: str,
    *,
    case_sensitive: bool = False,
) -> List[SearchResult]:
    """Return all entries whose value matches *pattern* (regex)."""
    flags = 0 if case_sensitive else re.IGNORECASE
    rx = re.compile(pattern, flags)
    results: List[SearchResult] = []
    for snap in snapshots:
        label = snap.get("label", "")
        for key, value in snap.get("env", {}).items():
            if rx.search(value):
                results.append(SearchResult(label=label, key=key, value=value))
    return results


def search_snapshots(
    snapshots: List[Dict],
    key_pattern: Optional[str] = None,
    value_pattern: Optional[str] = None,
    *,
    case_sensitive: bool = False,
) -> List[SearchResult]:
    """Search by key pattern, value pattern, or both (AND logic)."""
    if not key_pattern and not value_pattern:
        return []
    results: List[SearchResult] = []
    flags = 0 if case_sensitive else re.IGNORECASE
    key_rx = re.compile(key_pattern, flags) if key_pattern else None
    val_rx = re.compile(value_pattern, flags) if value_pattern else None
    for snap in snapshots:
        label = snap.get("label", "")
        for key, value in snap.get("env", {}).items():
            if key_rx and not key_rx.search(key):
                continue
            if val_rx and not val_rx.search(value):
                continue
            results.append(SearchResult(label=label, key=key, value=value))
    return results
