"""CLI commands for deduplicating environment snapshots by value."""
from __future__ import annotations
import argparse
import json
import os

from envsnap.env_dedup import dedup_snapshot, dedup_summary
from envsnap.snapshot import load, save


def cmd_dedup(args: argparse.Namespace) -> None:
    if args.file:
        snap = load(args.file)
    else:
        snap = dict(os.environ)

    result = dedup_snapshot(
        snap,
        keep=args.keep,
        ignore_empty=not args.include_empty,
    )

    if args.dry_run:
        print(dedup_summary(result))
        if result.removed:
            print("\nKeys that would be removed:")
            for k in result.removed:
                print(f"  {k}")
        return

    if args.output:
        save(result.snapshot, args.output)
        print(f"Saved deduplicated snapshot to {args.output}")
    else:
        print(json.dumps(result.snapshot, indent=2, sort_keys=True))

    print(dedup_summary(result))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envsnap dedup",
        description="Remove environment keys with duplicate values.",
    )
    parser.add_argument("--file", "-f", help="Path to snapshot JSON file.")
    parser.add_argument("--output", "-o", help="Write result to this file.")
    parser.add_argument(
        "--keep",
        choices=["first", "last"],
        default="first",
        help="Which key to keep when duplicates found (default: first).",
    )
    parser.add_argument(
        "--include-empty",
        action="store_true",
        help="Treat empty-string values as duplicates too.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without writing output.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    cmd_dedup(args)


if __name__ == "__main__":
    main()
