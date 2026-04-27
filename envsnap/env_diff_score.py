"""Compute a numeric similarity/divergence score between two snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from envsnap.diff import DiffResult, compare


@dataclass
class DiffScore:
    """Numeric score describing how different two snapshots are."""

    label_a: str
    label_b: str
    total_keys: int
    added: int
    removed: int
    changed: int
    unchanged: int
    # 0.0 = identical, 1.0 = completely different
    divergence: float
    # 0.0 = nothing in common, 1.0 = identical
    similarity: float
    breakdown: Dict[str, float] = field(default_factory=dict)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"DiffScore({self.label_a!r} vs {self.label_b!r}, "
            f"similarity={self.similarity:.2%}, divergence={self.divergence:.2%})"
        )


def score(snap_a: dict, snap_b: dict) -> DiffScore:
    """Return a DiffScore comparing *snap_a* and *snap_b*."""
    result: DiffResult = compare(snap_a, snap_b)

    n_added = len(result.added)
    n_removed = len(result.removed)
    n_changed = len(result.changed)
    n_unchanged = len(result.unchanged)
    total = n_added + n_removed + n_changed + n_unchanged

    if total == 0:
        divergence = 0.0
        similarity = 1.0
    else:
        changed_weight = n_added + n_removed + n_changed
        divergence = changed_weight / total
        similarity = 1.0 - divergence

    breakdown = {
        "added_ratio": n_added / total if total else 0.0,
        "removed_ratio": n_removed / total if total else 0.0,
        "changed_ratio": n_changed / total if total else 0.0,
        "unchanged_ratio": n_unchanged / total if total else 0.0,
    }

    label_a = snap_a.get("label", "snapshot_a")
    label_b = snap_b.get("label", "snapshot_b")

    return DiffScore(
        label_a=label_a,
        label_b=label_b,
        total_keys=total,
        added=n_added,
        removed=n_removed,
        changed=n_changed,
        unchanged=n_unchanged,
        divergence=round(divergence, 6),
        similarity=round(similarity, 6),
        breakdown=breakdown,
    )


def score_summary(ds: DiffScore) -> str:
    """Return a human-readable one-line summary of a DiffScore."""
    return (
        f"{ds.label_a} vs {ds.label_b}: "
        f"similarity={ds.similarity:.1%}  "
        f"(+{ds.added} -{ds.removed} ~{ds.changed} ={ds.unchanged})"
    )
