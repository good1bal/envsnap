"""Format watch session results for display."""
from __future__ import annotations

from typing import List

from envsnap.watch import WatchSession, WatchEvent


def _fmt_event(event: WatchEvent, index: int) -> List[str]:
    lines = [f"  Change #{index + 1} at poll {event.poll_index} (t={event.timestamp:.2f})"]
    for key in sorted(event.diff.added):
        lines.append(f"    + {key}")
    for key in sorted(event.diff.removed):
        lines.append(f"    - {key}")
    for key, (old, new) in sorted(event.diff.changed.items()):
        lines.append(f"    ~ {key}: {old!r} -> {new!r}")
    return lines


def format_watch_report(session: WatchSession) -> str:
    lines = [
        f"Watch session: {session.label}",
        f"Polls: {session.polls}  Interval: {session.interval}s",
        f"Change events: {len(session.events)}",
    ]
    if not session.events:
        lines.append("  No changes detected.")
    else:
        for i, event in enumerate(session.events):
            lines.extend(_fmt_event(event, i))
    return "\n".join(lines)


def watch_summary(session: WatchSession) -> str:
    if not session.has_changes():
        return f"[{session.label}] No changes in {session.polls} polls."
    return (
        f"[{session.label}] {len(session.events)} change event(s), "
        f"{session.total_changes()} total key changes over {session.polls} polls."
    )
