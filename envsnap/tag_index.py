"""Build and query an index of snapshots by tag."""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from envsnap.annotate import get_annotation


TagIndex = Dict[str, List[str]]  # tag -> list of snapshot labels


def build_tag_index(snapshots: list) -> TagIndex:
    """Build a mapping from tag to snapshot labels.

    Args:
        snapshots: list of snapshot dicts (as returned by capture/load).

    Returns:
        dict mapping each tag to a sorted list of snapshot labels.
    """
    index: TagIndex = defaultdict(list)
    for snap in snapshots:
        ann = get_annotation(snap)
        if ann is None:
            continue
        label = snap.get("label", "")
        for tag in ann.tags:
            index[tag].append(label)
    return {tag: sorted(labels) for tag, labels in index.items()}


def snapshots_for_tag(index: TagIndex, tag: str) -> List[str]:
    """Return snapshot labels that carry *tag*."""
    return index.get(tag, [])


def all_tags(index: TagIndex) -> List[str]:
    """Return sorted list of all known tags."""
    return sorted(index.keys())


def merge_indexes(*indexes: TagIndex) -> TagIndex:
    """Merge multiple TagIndex dicts into one, deduplicating labels."""
    merged: TagIndex = defaultdict(set)
    for idx in indexes:
        for tag, labels in idx.items():
            merged[tag].update(labels)
    return {tag: sorted(labels) for tag, labels in merged.items()}
