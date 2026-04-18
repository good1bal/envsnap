"""Watch for environment variable changes between two points in time."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from envsnap.snapshot import capture
from envsnap.diff import compare, DiffResult


@dataclass
class WatchEvent:
    timestamp: float
    diff: DiffResult
    poll_index: int


@dataclass
class WatchSession:
    label: str
    interval: float
    events: List[WatchEvent] = field(default_factory=list)
    polls: int = 0

    def has_changes(self) -> bool:
        return len(self.events) > 0

    def total_changes(self) -> int:
        return sum(
            len(e.diff.added) + len(e.diff.removed) + len(e.diff.changed)
            for e in self.events
        )


def watch(
    label: str = "watch",
    interval: float = 2.0,
    max_polls: int = 10,
    on_change: Optional[Callable[[WatchEvent], None]] = None,
    exclude_prefixes: Optional[List[str]] = None,
) -> WatchSession:
    """Poll environment variables and emit events when changes are detected."""
    session = WatchSession(label=label, interval=interval)
    previous = capture(label=label, exclude_prefixes=exclude_prefixes or [])

    for i in range(max_polls):
        time.sleep(interval)
        current = capture(label=label, exclude_prefixes=exclude_prefixes or [])
        diff = compare(previous, current)
        session.polls += 1

        if diff.added or diff.removed or diff.changed:
            event = WatchEvent(timestamp=time.time(), diff=diff, poll_index=i)
            session.events.append(event)
            if on_change:
                on_change(event)

        previous = current

    return session
