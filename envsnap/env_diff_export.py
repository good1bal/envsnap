"""Export diff results to various formats (JSON, CSV, Markdown)."""
from __future__ import annotations

import csv
import io
import json
from copy import deepcopy
from typing import List, Tuple

from envsnap.diff import DiffResult
from envsnap.redact import redact


def _labels(result: DiffResult) -> Tuple[str, str]:
    return result.get("label_a") or "A", result.get("label_b") or "B"


def _changed_values(value) -> Tuple[str, str]:
    """Return before/after values for either legacy tuple or compare() dict shapes."""
    if isinstance(value, dict):
        return value.get("before"), value.get("after")
    before, after = value
    return before, after


def redacted_result(result: DiffResult, placeholder: str = "<redacted>") -> DiffResult:
    """Return a copy of *result* with sensitive-key values masked.

    This keeps the export layer safe for JSON/CSV/Markdown callers that use the
    lower-level diff result directly instead of the human compare_report path.
    """
    masked = deepcopy(result)

    for section in ("added", "removed", "unchanged"):
        values = masked.get(section, {})
        if values:
            masked[section] = redact(values, placeholder=placeholder)

    changed = {}
    for key, value in masked.get("changed", {}).items():
        before, after = _changed_values(value)
        redacted_pair = redact({key: before, f"{key}__after": after}, placeholder=placeholder)
        if isinstance(value, dict):
            changed[key] = {
                **value,
                "before": redacted_pair[key],
                "after": redacted_pair[f"{key}__after"],
            }
        else:
            changed[key] = (redacted_pair[key], redacted_pair[f"{key}__after"])
    masked["changed"] = changed

    return DiffResult(**masked)


def to_json(result: DiffResult, indent: int = 2, redact_sensitive: bool = False) -> str:
    """Serialise a DiffResult to a JSON string."""
    if redact_sensitive:
        result = redacted_result(result)
    label_a, label_b = _labels(result)
    data = {
        "label_a": label_a,
        "label_b": label_b,
        "added": result.get("added", {}),
        "removed": result.get("removed", {}),
        "changed": [
            {"key": k, "before": before, "after": after}
            for k, value in result.get("changed", {}).items()
            for before, after in [_changed_values(value)]
        ],
        "unchanged": list(result.get("unchanged", {}).keys()),
    }
    return json.dumps(data, indent=indent, sort_keys=True)


def to_csv(result: DiffResult, redact_sensitive: bool = False) -> str:
    """Serialise a DiffResult to a CSV string with columns: status, key, before, after."""
    if redact_sensitive:
        result = redacted_result(result)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["status", "key", "before", "after"])

    for key in sorted(result.get("added", {})):
        writer.writerow(["added", key, "", result["added"][key]])

    for key in sorted(result.get("removed", {})):
        writer.writerow(["removed", key, result["removed"][key], ""])

    for key in sorted(result.get("changed", {})):
        before, after = _changed_values(result["changed"][key])
        writer.writerow(["changed", key, before, after])

    for key in sorted(result.get("unchanged", {})):
        writer.writerow(["unchanged", key, result["unchanged"][key], result["unchanged"][key]])

    return buf.getvalue()


def to_markdown(result: DiffResult, redact_sensitive: bool = False) -> str:
    """Serialise a DiffResult to a Markdown table."""
    if redact_sensitive:
        result = redacted_result(result)
    lines: List[str] = []
    label_a, label_b = _labels(result)

    lines.append(f"## Diff: `{label_a}` → `{label_b}`")
    lines.append("")
    lines.append("| Status | Key | Before | After |")
    lines.append("|--------|-----|--------|-------|")

    for key in sorted(result.get("added", {})):
        lines.append(f"| added | `{key}` | | `{result['added'][key]}` |")

    for key in sorted(result.get("removed", {})):
        lines.append(f"| removed | `{key}` | `{result['removed'][key]}` | |")

    for key in sorted(result.get("changed", {})):
        before, after = _changed_values(result["changed"][key])
        lines.append(f"| changed | `{key}` | `{before}` | `{after}` |")

    for key in sorted(result.get("unchanged", {})):
        v = result["unchanged"][key]
        lines.append(f"| unchanged | `{key}` | `{v}` | `{v}` |")

    return "\n".join(lines) + "\n"
