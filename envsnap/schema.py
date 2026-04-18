"""Load and save validation schemas from JSON files."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Optional


SCHEMA_KEYS = ("required", "forbidden", "patterns", "nonempty")


def load_schema(path: str | Path) -> Dict:
    """Load a validation schema from a JSON file."""
    data = json.loads(Path(path).read_text())
    return {k: data[k] for k in SCHEMA_KEYS if k in data}


def save_schema(
    path: str | Path,
    required: Optional[List[str]] = None,
    forbidden: Optional[List[str]] = None,
    patterns: Optional[Dict[str, str]] = None,
    nonempty: Optional[List[str]] = None,
) -> None:
    """Persist a schema dict to a JSON file."""
    schema: Dict = {}
    if required:
        schema["required"] = required
    if forbidden:
        schema["forbidden"] = forbidden
    if patterns:
        schema["patterns"] = patterns
    if nonempty:
        schema["nonempty"] = nonempty
    Path(path).write_text(json.dumps(schema, indent=2, sort_keys=True))


def schema_from_snapshot(snapshot: Dict) -> Dict:
    """Derive a permissive schema from an existing snapshot (all keys required)."""
    env: Dict[str, str] = snapshot.get("env", {})
    return {"required": sorted(env.keys())}
