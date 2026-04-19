"""Lint environment variable snapshots against naming conventions."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict
import re


@dataclass
class LintIssue:
    key: str
    message: str
    severity: str = "warning"  # "error" | "warning"

    def __repr__(self) -> str:
        return f"LintIssue({self.severity}, {self.key!r}: {self.message})"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0


_UPPER_SNAKE = re.compile(r'^[A-Z][A-Z0-9_]*$')
_DOUBLE_UNDERSCORE = re.compile(r'__')


def lint_snapshot(
    snap: Dict[str, str],
    *,
    allow_lowercase: bool = False,
    max_value_length: int = 0,
    forbidden_patterns: List[str] | None = None,
) -> LintResult:
    result = LintResult()
    env = snap.get("env", {})

    for key, value in env.items():
        if not allow_lowercase and not _UPPER_SNAKE.match(key):
            result.issues.append(LintIssue(key, "Key should be UPPER_SNAKE_CASE", "warning"))

        if _DOUBLE_UNDERSCORE.search(key):
            result.issues.append(LintIssue(key, "Key contains double underscore", "warning"))

        if max_value_length and len(value) > max_value_length:
            result.issues.append(
                LintIssue(key, f"Value exceeds max length {max_value_length}", "warning")
            )

        if forbidden_patterns:
            for pat in forbidden_patterns:
                if re.search(pat, value):
                    result.issues.append(
                        LintIssue(key, f"Value matches forbidden pattern {pat!r}", "error")
                    )

    return result


def lint_summary(result: LintResult) -> str:
    if not result.issues:
        return "lint: no issues found"
    lines = [f"lint: {len(result.errors)} error(s), {len(result.warnings)} warning(s)"]
    for issue in result.issues:
        lines.append(f"  [{issue.severity}] {issue.key}: {issue.message}")
    return "\n".join(lines)
