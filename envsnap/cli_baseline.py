"""CLI commands for baseline management."""

from __future__ import annotations

import argparse
import sys

from envsnap.snapshot import capture
from envsnap.baseline import (
    set_baseline,
    load_baseline,
    clear_baseline,
    baseline_exists,
    diff_from_baseline,
)
from envsnap.diff import summary as diff_summary
from envsnap.diff import DiffResult


def cmd_set(args: argparse.Namespace) -> None:
    snap = capture(label=args.label)
    path = set_baseline(snap, args.file)
    print(f"Baseline saved to {path} (label={snap['label']}, checksum={snap['checksum']})")


def cmd_clear(args: argparse.Namespace) -> None:
    deleted = clear_baseline(args.file)
    if deleted:
        print("Baseline cleared.")
    else:
        print("No baseline found to clear.", file=sys.stderr)


def cmd_show(args: argparse.Namespace) -> None:
    try:
        snap = load_baseline(args.file)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    env = snap.get("env", {})
    print(f"Baseline: {snap.get('label')}  [{snap.get('timestamp')}]")
    for k, v in sorted(env.items()):
        print(f"  {k}={v}")


def cmd_diff(args: argparse.Namespace) -> None:
    if not baseline_exists(args.file):
        print("No baseline set. Run 'baseline set' first.", file=sys.stderr)
        sys.exit(1)
    current = capture(label="current")
    result = diff_from_baseline(current, args.file)
    dr = DiffResult(
        added=result["added"],
        removed=result["removed"],
        changed=result["changed"],
        unchanged=result["unchanged"],
    )
    print(diff_summary(dr))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="envsnap baseline")
    parser.add_argument("--file", default=None, help="Baseline file path")
    sub = parser.add_subparsers(dest="command")

    p_set = sub.add_parser("set", help="Capture and save current env as baseline")
    p_set.add_argument("--label", default="baseline")
    p_set.set_defaults(func=cmd_set)

    p_clear = sub.add_parser("clear", help="Delete the baseline")
    p_clear.set_defaults(func=cmd_clear)

    p_show = sub.add_parser("show", help="Print baseline contents")
    p_show.set_defaults(func=cmd_show)

    p_diff = sub.add_parser("diff", help="Diff current env against baseline")
    p_diff.set_defaults(func=cmd_diff)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
