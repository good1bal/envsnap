"""Multi-snapshot comparison: compare more than two snapshots at once.

Provides a side-by-side view of keys across N snapshots, showing which
snapshots contain each key and what value each holds.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class MultiKeyEntry:
    """Represents a single key's presence and values across multiple snapshots."""

    key: str
    # label -> value or None if the key is absent in that snapshot
    values: Dict[str, Optional[str]] = field(default_factory=dict)

    @property
    def present_in(self) -> List[str]:
        """Labels of snapshots that contain this key."""
        return [label for label, val in self.values.items() if val is not None]

    @property
    def absent_in(self) -> List[str]:
        """Labels of snapshots that do NOT contain this key."""
        return [label for label, val in self.values.items() if val is None]

    @property
    def is_uniform(self) -> bool:
        """True if every snapshot that has this key shares the same value."""
        present_vals = [v for v in self.values.values() if v is not None]
        return len(set(present_vals)) <= 1

    @property
    def is_universal(self) -> bool:
        """True if all snapshots contain this key."""
        return all(v is not None for v in self.values.values())

    def __repr__(self) -> str:  # pragma: no cover
        status = "uniform" if self.is_uniform else "diverged"
        return f"<MultiKeyEntry key={self.key!r} {status} present={self.present_in}>"


@dataclass
class MultiCompareResult:
    """Result of comparing N snapshots."""

    labels: List[str]
    entries: List[MultiKeyEntry] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.entries)

    def keys_in_all(self) -> List[MultiKeyEntry]:
        """Entries present in every snapshot."""
        return [e for e in self.entries if e.is_universal]

    def keys_in_some(self) -> List[MultiKeyEntry]:
        """Entries present in at least one but not all snapshots."""
        return [e for e in self.entries if not e.is_universal]

    def diverged_keys(self) -> List[MultiKeyEntry]:
        """Universal keys whose values differ across snapshots."""
        return [e for e in self.keys_in_all() if not e.is_uniform]

    def uniform_keys(self) -> List[MultiKeyEntry]:
        """Universal keys that share the same value in every snapshot."""
        return [e for e in self.keys_in_all() if e.is_uniform]


def compare_multi(
    snapshots: List[Dict[str, str]],
    labels: Optional[List[str]] = None,
) -> MultiCompareResult:
    """Compare multiple environment snapshots side by side.

    Args:
        snapshots: List of env dicts (each mapping key -> value).
        labels: Optional display labels for each snapshot.  Defaults to
                "snap_0", "snap_1", …

    Returns:
        A :class:`MultiCompareResult` with one entry per unique key.
    """
    if not snapshots:
        return MultiCompareResult(labels=[])

    if labels is None:
        labels = [f"snap_{i}" for i in range(len(snapshots))]

    if len(labels) != len(snapshots):
        raise ValueError(
            f"labels length ({len(labels)}) must match snapshots length ({len(snapshots)})"
        )

    # Collect all unique keys across every snapshot
    all_keys: Set[str] = set()
    for snap in snapshots:
        all_keys.update(snap.keys())

    entries: List[MultiKeyEntry] = []
    for key in sorted(all_keys):
        values = {label: snap.get(key) for label, snap in zip(labels, snapshots)}
        entries.append(MultiKeyEntry(key=key, values=values))

    return MultiCompareResult(labels=labels, entries=entries)


def multi_compare_summary(result: MultiCompareResult) -> str:
    """Return a human-readable summary of a multi-snapshot comparison."""
    total = len(result)
    universal = len(result.keys_in_all())
    partial = len(result.keys_in_some())
    diverged = len(result.diverged_keys())

    lines = [
        f"Snapshots compared : {len(result.labels)} ({', '.join(result.labels)})",
        f"Total unique keys  : {total}",
        f"Present in all     : {universal}",
        f"Present in some    : {partial}",
        f"Diverged values    : {diverged}",
    ]
    return "\n".join(lines)
