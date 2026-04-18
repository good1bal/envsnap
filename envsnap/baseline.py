"""Baseline management: mark a snapshot as the reference point for future comparisons."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envsnap.snapshot import load, save

_DEFAULT_BASELINE_FILE = ".envsnap_baseline.json"


def _baseline_path(path: Optional[str] = None) -> Path:
    return Path(path or _DEFAULT_BASELINE_FILE)


def set_baseline(snapshot: dict, path: Optional[str] = None) -> Path:
    """Persist snapshot as the current baseline. Returns the file path used."""
    dest = _baseline_path(path)
    save(snapshot, str(dest))
    return dest


def load_baseline(path: Optional[str] = None) -> dict:
    """Load the baseline snapshot. Raises FileNotFoundError if none exists."""
    dest = _baseline_path(path)
    if not dest.exists():
        raise FileNotFoundError(f"No baseline found at {dest}")
    return load(str(dest))


def clear_baseline(path: Optional[str] = None) -> bool:
    """Delete the baseline file. Returns True if deleted, False if not found."""
    dest = _baseline_path(path)
    if dest.exists():
        dest.unlink()
        return True
    return False


def baseline_exists(path: Optional[str] = None) -> bool:
    return _baseline_path(path).exists()


def diff_from_baseline(snapshot: dict, path: Optional[str] = None) -> dict:
    """Compare snapshot against baseline. Returns compare result dict."""
    from envsnap.diff import compare
    baseline = load_baseline(path)
    result = compare(baseline, snapshot)
    return {
        "added": result.added,
        "removed": result.removed,
        "changed": result.changed,
        "unchanged": result.unchanged,
    }
