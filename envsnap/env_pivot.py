"""Pivot environment snapshots: transpose keys/labels into a comparison table."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PivotRow:
    key: str
    values: Dict[str, Optional[str]]  # label -> value

    def is_uniform(self) -> bool:
        """Return True if all present values are identical."""
        vals = [v for v in self.values.values() if v is not None]
        return len(set(vals)) <= 1

    def missing_in(self) -> List[str]:
        """Labels where this key is absent."""
        return [label for label, v in self.values.items() if v is None]

    def __repr__(self) -> str:  # pragma: no cover
        return f"PivotRow(key={self.key!r}, uniform={self.is_uniform()})"


@dataclass
class PivotTable:
    labels: List[str]
    rows: List[PivotRow] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.rows)

    def uniform_rows(self) -> List[PivotRow]:
        return [r for r in self.rows if r.is_uniform()]

    def differing_rows(self) -> List[PivotRow]:
        return [r for r in self.rows if not r.is_uniform()]


def build_pivot(snapshots: Dict[str, Dict[str, str]]) -> PivotTable:
    """Build a PivotTable from a mapping of label -> env dict."""
    labels = list(snapshots.keys())
    all_keys: List[str] = sorted(
        {k for env in snapshots.values() for k in env}
    )
    rows = [
        PivotRow(
            key=key,
            values={label: snapshots[label].get(key) for label in labels},
        )
        for key in all_keys
    ]
    return PivotTable(labels=labels, rows=rows)


def pivot_summary(table: PivotTable) -> str:
    """Return a human-readable summary of the pivot table."""
    total = len(table)
    uniform = len(table.uniform_rows())
    differing = len(table.differing_rows())
    return (
        f"Pivot: {total} keys across {len(table.labels)} snapshots — "
        f"{uniform} uniform, {differing} differing"
    )
