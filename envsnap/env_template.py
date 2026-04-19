"""Generate and apply environment variable templates."""
from __future__ import annotations

from typing import Any


class TemplateMissingKey(KeyError):
    pass


def build_template(snapshot: dict[str, Any]) -> dict[str, str]:
    """Build a template from a snapshot, replacing values with empty strings."""
    env = snapshot.get("env", {})
    return {k: "" for k in env}


def apply_template(
    template: dict[str, str],
    values: dict[str, str],
    allow_missing: bool = False,
) -> dict[str, str]:
    """Fill a template with provided values.

    Args:
        template: keys with empty-string placeholders.
        values: mapping of key -> value to fill in.
        allow_missing: if False, raises TemplateMissingKey for unfilled keys.

    Returns:
        Filled template dict.
    """
    result: dict[str, str] = {}
    for key in template:
        if key in values:
            result[key] = values[key]
        elif not allow_missing:
            raise TemplateMissingKey(f"Missing value for template key: {key!r}")
        else:
            result[key] = ""
    return result


def template_diff(template: dict[str, str], snapshot: dict[str, Any]) -> dict[str, list[str]]:
    """Return keys that are in template but missing from snapshot env, and vice-versa."""
    env_keys = set(snapshot.get("env", {}).keys())
    tmpl_keys = set(template.keys())
    return {
        "missing_in_snapshot": sorted(tmpl_keys - env_keys),
        "extra_in_snapshot": sorted(env_keys - tmpl_keys),
    }


def template_summary(diff: dict[str, list[str]]) -> str:
    missing = diff.get("missing_in_snapshot", [])
    extra = diff.get("extra_in_snapshot", [])
    lines = []
    if missing:
        lines.append(f"Missing in snapshot ({len(missing)}): {', '.join(missing)}")
    if extra:
        lines.append(f"Extra in snapshot ({len(extra)}): {', '.join(extra)}")
    if not lines:
        return "Template matches snapshot."
    return "\n".join(lines)
