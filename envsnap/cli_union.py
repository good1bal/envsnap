"""CLI commands for env union."""
from __future__ import annotations
import argparse
import json
import sys
from envsnap.env_union import union, union_summary, UnionConflict
from envsnap.export import from_json


def cmd_union(args: argparse.Namespace) -> None:
    snapshots = []
    for path in args.files:
        try:
            with open(path) as fh:
                snap = from_json(fh.read())
            snapshots.append(snap)
        except FileNotFoundError:
            print(f"error: file not found: {path}", file=sys.stderr)
            sys.exit(1)

    try:
        result = union(snapshots, strategy=args.strategy)
    except UnionConflict as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)

    if args.summary:
        print(union_summary(result))
        return

    if args.output:
        data = {"label": args.label or "union", "env": result.env}
        with open(args.output, "w") as fh:
            json.dump(data, fh, indent=2, sort_keys=True)
        print(f"Written to {args.output}")
    else:
        for k, v in sorted(result.env.items()):
            print(f"{k}={v}")

    if result.conflicts:
        print(f"\nWarning: {len(result.conflicts)} conflict(s) resolved via '{args.strategy}' strategy.",
              file=sys.stderr)


def build_parser(parent: argparse._SubParsersAction | None = None):
    desc = "Union multiple snapshot files into one environment."
    if parent is not None:
        p = parent.add_parser("union", help=desc)
    else:
        p = argparse.ArgumentParser(prog="envsnap-union", description=desc)
    p.add_argument("files", nargs="+", metavar="FILE", help="Snapshot JSON files")
    p.add_argument("--strategy", choices=["first", "last", "error"], default="first")
    p.add_argument("--output", "-o", metavar="FILE", help="Write result to file")
    p.add_argument("--label", default="union", help="Label for output snapshot")
    p.add_argument("--summary", action="store_true", help="Print summary only")
    p.set_defaults(func=cmd_union)
    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
