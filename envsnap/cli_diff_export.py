"""CLI commands for exporting diff results to JSON, CSV, or Markdown."""
from __future__ import annotations

import argparse
import sys

from envsnap.diff import compare
from envsnap.env_diff_export import to_csv, to_json, to_markdown
from envsnap.snapshot import load


def cmd_diff_export(args: argparse.Namespace) -> None:
    """Load two snapshot files, diff them, and emit the result in the chosen format."""
    try:
        snap_a = load(args.snapshot_a)
    except FileNotFoundError:
        print(f"error: snapshot file not found: {args.snapshot_a}", file=sys.stderr)
        sys.exit(1)

    try:
        snap_b = load(args.snapshot_b)
    except FileNotFoundError:
        print(f"error: snapshot file not found: {args.snapshot_b}", file=sys.stderr)
        sys.exit(1)

    result = compare(snap_a, snap_b)

    fmt = args.format.lower()
    if fmt == "json":
        output = to_json(result, indent=args.indent)
    elif fmt == "csv":
        output = to_csv(result)
    elif fmt == "markdown":
        output = to_markdown(result)
    else:
        print(f"error: unknown format '{fmt}'. Choose json, csv, or markdown.", file=sys.stderr)
        sys.exit(1)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(output)
        print(f"Diff written to {args.output}")
    else:
        print(output, end="")


def build_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    description = "Export a diff between two snapshots to JSON, CSV, or Markdown."
    if parent is not None:
        parser = parent.add_parser("diff-export", help=description)
    else:
        parser = argparse.ArgumentParser(prog="envsnap-diff-export", description=description)

    parser.add_argument("snapshot_a", help="Path to the first (base) snapshot file.")
    parser.add_argument("snapshot_b", help="Path to the second (target) snapshot file.")
    parser.add_argument(
        "--format", "-f",
        default="json",
        choices=["json", "csv", "markdown"],
        help="Output format (default: json).",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation level (default: 2).",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Write output to this file instead of stdout.",
    )
    parser.set_defaults(func=cmd_diff_export)
    return parser


def main() -> None:  # pragma: no cover
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":  # pragma: no cover
    main()
