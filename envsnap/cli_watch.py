"""CLI commands for the watch feature."""
from __future__ import annotations

import sys
from typing import List, Optional

from envsnap.watch import watch, WatchEvent
from envsnap.watch_report import format_watch_report, watch_summary


def _on_change_printer(event: WatchEvent) -> None:
    keys = sorted(event.diff.added) + sorted(event.diff.removed) + sorted(event.diff.changed)
    print(f"[poll {event.poll_index}] change detected: {', '.join(keys)}", flush=True)


def cmd_watch(
    label: str = "watch",
    interval: float = 2.0,
    max_polls: int = 10,
    exclude_prefixes: Optional[List[str]] = None,
    verbose: bool = False,
    output: str = "summary",
) -> int:
    """Run a watch session and print results.

    Returns exit code: 0 if no changes, 1 if changes detected.
    """
    on_change = _on_change_printer if verbose else None

    session = watch(
        label=label,
        interval=interval,
        max_polls=max_polls,
        on_change=on_change,
        exclude_prefixes=exclude_prefixes,
    )

    if output == "full":
        print(format_watch_report(session))
    else:
        print(watch_summary(session))

    return 1 if session.has_changes() else 0


def main(argv: Optional[List[str]] = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Watch environment variables for changes.")
    parser.add_argument("--label", default="watch")
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--max-polls", type=int, default=10)
    parser.add_argument("--exclude", nargs="*", default=[])
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--output", choices=["summary", "full"], default="summary")
    args = parser.parse_args(argv)

    code = cmd_watch(
        label=args.label,
        interval=args.interval,
        max_polls=args.max_polls,
        exclude_prefixes=args.exclude,
        verbose=args.verbose,
        output=args.output,
    )
    sys.exit(code)
