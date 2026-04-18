"""Export snapshots to various output formats."""

from __future__ import annotations

import json
import csv
import io
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from envsnap.snapshot import Snapshot


def to_json(snapshot: dict, indent: int = 2) -> str:
    """Serialize a snapshot to a JSON string."""
    return json.dumps(snapshot, indent=indent, sort_keys=True)


def to_dotenv(snapshot: dict) -> str:
    """Serialize snapshot env vars to .env file format.

    Only the 'vars' section is exported; metadata is omitted.
    """
    lines = []
    for key, value in sorted(snapshot.get("vars", {}).items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines) + ("\n" if lines else "")


def to_csv(snapshot: dict) -> str:
    """Serialize snapshot env vars to CSV format (key, value rows)."""
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["key", "value"])
    for key, value in sorted(snapshot.get("vars", {}).items()):
        writer.writerow([key, value])
    return output.getvalue()


def from_json(data: str) -> dict:
    """Deserialize a snapshot from a JSON string."""
    snapshot = json.loads(data)
    if "vars" not in snapshot:
        raise ValueError("Invalid snapshot: missing 'vars' key")
    return snapshot
