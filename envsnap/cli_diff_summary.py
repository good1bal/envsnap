"""CLI command for displaying a high-level diff summary between two snapshots."""
import argparse
import sys
from envsnap.export import from_json
from envsnap.env_diff_summary import build_diff_summary, format_diff_summary


def cmd_diff_summary(args: argparse.Namespace) -> None:
    try:
        with open(args.file_a) as f:
            snap_a = from_json(f.read())
    except FileNotFoundError:
        print(f"Error: file not found: {args.file_a}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.file_b) as f:
            snap_b = from_json(f.read())
    except FileNotFoundError:
        print(f"Error: file not found: {args.file_b}", file=sys.stderr)
        sys.exit(1)

    report = build_diff_summary(snap_a, snap_b)
    print(format_diff_summary(report))

    if args.exit_code and report.stats.total_changes > 0:
        sys.exit(1)


def build_parser(parent=None) -> argparse.ArgumentParser:
    if parent:
        parser = parent.add_parser(
            "diff-summary",
            help="Show a high-level summary of differences between two snapshots",
        )
    else:
        parser = argparse.ArgumentParser(
            prog="envsnap diff-summary",
            description="Show a high-level summary of differences between two snapshots",
        )
    parser.add_argument("file_a", help="Path to first snapshot JSON file")
    parser.add_argument("file_b", help="Path to second snapshot JSON file")
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 if there are any changes",
    )
    parser.set_defaults(func=cmd_diff_summary)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
