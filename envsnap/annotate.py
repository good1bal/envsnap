"""Attach user-defined annotations (tags/notes) to snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Annotation:
    label: str
    note: str = ""
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"label": self.label, "note": self.note, "tags": self.tags}

    @classmethod
    def from_dict(cls, data: dict) -> "Annotation":
        return cls(
            label=data["label"],
            note=data.get("note", ""),
            tags=data.get("tags", []),
        )


def annotate(snapshot: dict, note: str = "", tags: Optional[List[str]] = None) -> dict:
    """Return a copy of *snapshot* with an annotation block attached."""
    ann = Annotation(
        label=snapshot.get("label", "unknown"),
        note=note,
        tags=tags or [],
    )
    return {**snapshot, "annotation": ann.to_dict()}


def get_annotation(snapshot: dict) -> Optional[Annotation]:
    """Extract the Annotation from a snapshot, or None if absent."""
    raw = snapshot.get("annotation")
    if raw is None:
        return None
    return Annotation.from_dict(raw)


def filter_by_tag(snapshots: List[dict], tag: str) -> List[dict]:
    """Return only snapshots whose annotation includes *tag*."""
    result = []
    for snap in snapshots:
        ann = get_annotation(snap)
        if ann and tag in ann.tags:
            result.append(snap)
    return result


def annotation_summary(snapshot: dict) -> str:
    """Human-readable one-liner for a snapshot's annotation."""
    ann = get_annotation(snapshot)
    if ann is None:
        return "(no annotation)"
    tag_str = ", ".join(ann.tags) if ann.tags else "—"
    return f"note: {ann.note or '—'}  tags: [{tag_str}]"
