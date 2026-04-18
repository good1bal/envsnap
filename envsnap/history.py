"""History management: store and retrieve ordered snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from envsnap.snapshot import load, save

DEFAULT_HISTORY_FILE = ".envsnap_history.json"


def _history_path(path: Optional[str] = None) -> Path:
    return Path(path or DEFAULT_HISTORY_FILE)


def load_history(path: Optional[str] = None) -> List[dict]:
    """Return list of snapshot dicts ordered oldest-first."""
    p = _history_path(path)
    if not p.exists():
        return []
    with p.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def save_history(history: List[dict], path: Optional[str] = None) -> None:
    """Persist history list to disk."""
    p = _history_path(path)
    with p.open("w", encoding="utf-8") as fh:
        json.dump(history, fh, indent=2)


def append_snapshot(snapshot: dict, path: Optional[str] = None) -> List[dict]:
    """Append *snapshot* to history and persist; returns updated history."""
    history = load_history(path)
    history.append(snapshot)
    save_history(history, path)
    return history


def get_snapshot(label: str, path: Optional[str] = None) -> Optional[dict]:
    """Return the first snapshot matching *label*, or None."""
    for snap in load_history(path):
        if snap.get("label") == label:
            return snap
    return None


def latest_snapshot(path: Optional[str] = None) -> Optional[dict]:
    """Return the most-recently appended snapshot, or None."""
    history = load_history(path)
    return history[-1] if history else None


def list_labels(path: Optional[str] = None) -> List[str]:
    """Return ordered list of labels present in history."""
    return [s.get("label", "") for s in load_history(path)]
