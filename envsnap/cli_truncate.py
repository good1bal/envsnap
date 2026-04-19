"""CLI commands for truncating env snapshot values."""
from __future__ import annotations
import argparse
import sys

from envsnap.env_truncate import truncate_values, truncate_summary
from envsnap.snapshot import load, save


def cmd_truncate(args: argparse.Namespace) -> None:
    """Load a snapshot, truncate long values, and save or print the result."""
    try:
        snap = load(args.file)
    except FileNotFoundError:
        print(f"Error: snapshot file '{args.file}' not found.", file=sys.stderr)
        sys.exit(1)

    keys = args.keys if args.keys else None
    suffix = args.suffix if args.suffix is not None else "..."

    try:
        result = truncate_values(
            snap["env"],
            max_length=args.max_length,
            suffix=suffix,
            keys=keys,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(truncate_summary(result))

    if args.dry_run:
        return

    out_file = args.output or args.file
    snap["env"] = result.snapshot
    save(snap, out_file)
    print(f"Saved to {out_file}")


def build_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    desc = "Truncate long environment variable values in a snapshot."
    if parent is not None:
        p = parent.add_parser("truncate", help=desc)
    else:
        p = argparse.ArgumentParser(prog="envsnap-truncate", description=desc)

    p.add_argument("file", help="Path to the snapshot JSON file.")
    p.add_argument(
        "--max-length", type=int, required=True, dest="max_length",
        help="Maximum value length (inclusive).",
    )
    p.add_argument(
        "--suffix", default="...",
        help="Suffix appended to truncated values (default: '...').",
    )
    p.add_argument(
        "--keys", nargs="+", default=None,
        help="Limit truncation to these keys.",
    )
    p.add_argument(
        "--output", default=None,
        help="Output file path (defaults to overwriting input file).",
    )
    p.add_argument(
        "--dry-run", action="store_true", dest="dry_run",
        help="Print summary without saving.",
    )
    p.set_defaults(func=cmd_truncate)
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
