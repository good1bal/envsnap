"""Highlight changed characters between two string values in a diff."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
import difflib


@dataclass
class HighlightSpan:
    """A segment of text with an optional change marker."""
    text: str
    changed: bool = False

    def __repr__(self) -> str:  # pragma: no cover
        marker = "*" if self.changed else " "
        return f"HighlightSpan({marker!r}, {self.text!r})"


@dataclass
class HighlightResult:
    """Character-level diff between old_value and new_value."""
    key: str
    old_spans: List[HighlightSpan] = field(default_factory=list)
    new_spans: List[HighlightSpan] = field(default_factory=list)

    def __repr__(self) -> str:
        return (
            f"HighlightResult(key={self.key!r}, "
            f"old_spans={len(self.old_spans)}, new_spans={len(self.new_spans)})"
        )


def _spans_from_opcodes(
    opcodes: list, a: str, b: str
) -> tuple[List[HighlightSpan], List[HighlightSpan]]:
    old_spans: List[HighlightSpan] = []
    new_spans: List[HighlightSpan] = []
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == "equal":
            old_spans.append(HighlightSpan(a[i1:i2], changed=False))
            new_spans.append(HighlightSpan(b[j1:j2], changed=False))
        elif tag == "replace":
            old_spans.append(HighlightSpan(a[i1:i2], changed=True))
            new_spans.append(HighlightSpan(b[j1:j2], changed=True))
        elif tag == "delete":
            old_spans.append(HighlightSpan(a[i1:i2], changed=True))
        elif tag == "insert":
            new_spans.append(HighlightSpan(b[j1:j2], changed=True))
    return old_spans, new_spans


def highlight_diff(key: str, old_value: str, new_value: str) -> HighlightResult:
    """Compute character-level highlights between old_value and new_value."""
    matcher = difflib.SequenceMatcher(None, old_value, new_value, autojunk=False)
    opcodes = matcher.get_opcodes()
    old_spans, new_spans = _spans_from_opcodes(opcodes, old_value, new_value)
    return HighlightResult(key=key, old_spans=old_spans, new_spans=new_spans)


def highlight_summary(result: HighlightResult) -> str:
    """Return a compact human-readable summary of the highlighted diff."""
    old_str = "".join(
        f"[{s.text}]" if s.changed else s.text for s in result.old_spans
    )
    new_str = "".join(
        f"[{s.text}]" if s.changed else s.text for s in result.new_spans
    )
    return f"{result.key}: {old_str!r} -> {new_str!r}"


def highlight_many(
    changed: dict[str, tuple[str, str]]
) -> List[HighlightResult]:
    """Highlight multiple changed keys. changed maps key -> (old, new)."""
    return [highlight_diff(k, old, new) for k, (old, new) in changed.items()]
