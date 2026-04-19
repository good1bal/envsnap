"""CLI commands for snapshot intersection."""
from __future__ import annotations
import argparse
import json
from typing import List

from envsnap.snapshot import load
from envsnap.env_intersect import intersect, intersect_summary


def cmd_intersect(args: argparse.Namespace) -> None:
    snapshots = []
    for path in args.files:
        snap = load(path)
        snapshots.append(snap.get("env", snap))

    if len(snapshots) < 2:
        print("[error] At least two snapshot files required.")
        raise SystemExit(1)

    result = intersect(snapshots)

    if args.json:
        output = {
            "agreed": result.agreed,
            "conflicted": result.conflicted,
        }
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print(intersect_summary(result))

    if args.fail_on_conflict and result.conflicted:
        raise SystemExit(2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envsnap intersect",
        description="Show common keys across multiple snapshots.",
    )
    parser.add_argument("files", nargs="+", metavar="FILE",
                        help="Snapshot files to intersect")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    parser.add_argument("--fail-on-conflict", action="store_true",
                        help="Exit with code 2 if any conflicted keys found")
    return parser


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    cmd_intersect(args)


if __name__ == "__main__":
    main()
