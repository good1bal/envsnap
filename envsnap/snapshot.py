"""Core snapshot functionality for capturing environment variables."""

import os
import json
import hashlib
from datetime import datetime, timezone
from typing import Optional


def capture(label: Optional[str] = None, exclude_prefixes: tuple = ()) -> dict:
    """Capture current environment variables into a snapshot dict."""
    env = {
        key: value
        for key, value in os.environ.items()
        if not any(key.startswith(prefix) for prefix in exclude_prefixes)
    }

    snapshot = {
        "label": label or "snapshot",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "env": env,
        "checksum": _checksum(env),
    }
    return snapshot


def save(snapshot: dict, path: str) -> None:
    """Persist a snapshot to a JSON file."""
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(snapshot, fh, indent=2, sort_keys=True)


def load(path: str) -> dict:
    """Load a snapshot from a JSON file."""
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _checksum(env: dict) -> str:
    """Compute a stable SHA-256 checksum over sorted env key=value pairs."""
    payload = "\n".join(f"{k}={v}" for k, v in sorted(env.items()))
    return hashlib.sha256(payload.encode()).hexdigest()
