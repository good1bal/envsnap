"""Validate snapshots against a schema of required/forbidden keys and value rules."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class ValidationIssue:
    key: str
    severity: str  # 'error' | 'warning'
    message: str


@dataclass
class ValidationResult:
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    @property
    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]


def validate(
    snapshot: Dict,
    required: Optional[List[str]] = None,
    forbidden: Optional[List[str]] = None,
    patterns: Optional[Dict[str, str]] = None,
    nonempty: Optional[List[str]] = None,
) -> ValidationResult:
    """Validate a snapshot dict against rules.

    Args:
        snapshot: snapshot dict (as returned by capture/load).
        required: keys that must be present.
        forbidden: keys that must not be present.
        patterns: mapping of key -> regex; value must match if key present.
        nonempty: keys whose values must not be empty strings.
    """
    env: Dict[str, str] = snapshot.get("env", {})
    issues: List[ValidationIssue] = []

    for key in required or []:
        if key not in env:
            issues.append(ValidationIssue(key=key, severity="error",
                                          message=f"Required key '{key}' is missing."))

    for key in forbidden or []:
        if key in env:
            issues.append(ValidationIssue(key=key, severity="error",
                                          message=f"Forbidden key '{key}' is present."))

    for key, pattern in (patterns or {}).items():
        if key in env:
            if not re.fullmatch(pattern, env[key]):
                issues.append(ValidationIssue(key=key, severity="error",
                                              message=f"Value for '{key}' does not match pattern '{pattern}'."))

    for key in nonempty or []:
        if key in env and env[key] == "":
            issues.append(ValidationIssue(key=key, severity="warning",
                                          message=f"Key '{key}' is present but empty."))

    return ValidationResult(issues=issues)


def validation_summary(result: ValidationResult) -> str:
    if result.valid and not result.warnings:
        return "OK: snapshot is valid."
    lines = []
    for issue in result.issues:
        lines.append(f"[{issue.severity.upper()}] {issue.key}: {issue.message}")
    status = "INVALID" if not result.valid else "WARNINGS"
    return f"{status}\n" + "\n".join(lines)
