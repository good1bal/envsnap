"""CLI commands for searching environment snapshots."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envsnap.env_search import SearchResult, search_snapshots
from envsnap.snapshot import load


def _format_results(results: List[SearchResult]) -> str:
    if not results:
        return "No matches found."
    lines = []
    current_label = None
    for r in results:
        if r.label != current_label:
            lines.append(f"[{r.label}]")
            current_label = r.label
        lines.append(f"  {r.key}={r.value}")
    return "\n".join(lines)


def cmd_search(args: argparse.Namespace) -> None:
    snapshots = []
    for path in args.files:
        try:
            snapshots.append(load(path))
        except FileNotFoundError:
            print(f"Warning: {path} not found, skipping.", file=sys.stderr)

    if not snapshots:
        print("No snapshots loaded.", file=sys.stderr)
        sys.exit(1)

    results = search_snapshots(
        snapshots,
        key_pattern=args.key or None,
        value_pattern=args.value or None,
        case_sensitive=args.case_sensitive,
    )
    print(_format_results(results))
    if not results:
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envsnap search",
        description="Search keys/values across snapshot files.",
    )
    parser.add_argument("files", nargs="+", help="Snapshot JSON files to search")
    parser.add_argument("--key", default="", help="Regex pattern to match against keys")
    parser.add_argument("--value", default="", help="Regex pattern to match against values")
    parser.add_argument(
        "--case-sensitive", action="store_true", help="Use case-sensitive matching"
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    cmd_search(args)


if __name__ == "__main__":
    main()
