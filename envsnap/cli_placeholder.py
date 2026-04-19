"""CLI commands for placeholder detection and resolution."""

from __future__ import annotations

import argparse
import json
import os
import sys

from envsnap.env_placeholder import (
    find_placeholders,
    resolve_placeholders,
    placeholder_summary,
)
from envsnap.snapshot import load, capture


def cmd_find(args: argparse.Namespace) -> None:
    if args.file:
        snap = load(args.file)
    else:
        snap = capture()
    keys = find_placeholders(snap)
    if not keys:
        print("No placeholders found.")
        return
    print(f"{len(keys)} placeholder(s) found:")
    for k in keys:
        print(f"  {k} = {snap[k]}")


def cmd_resolve(args: argparse.Namespace) -> None:
    if args.file:
        snap = load(args.file)
    else:
        snap = capture()

    overrides: dict = {}
    if args.override:
        for item in args.override:
            if "=" not in item:
                print(f"Invalid override (expected KEY=VALUE): {item}", file=sys.stderr)
                sys.exit(1)
            k, v = item.split("=", 1)
            overrides[k] = v
    if args.override_json:
        try:
            overrides.update(json.loads(args.override_json))
        except json.JSONDecodeError as exc:
            print(f"Invalid JSON: {exc}", file=sys.stderr)
            sys.exit(1)

    result = resolve_placeholders(snap, overrides)
    print(placeholder_summary(result))

    if args.out:
        from envsnap.snapshot import save
        save(result.snapshot, args.out)
        print(f"Saved to {args.out}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="envsnap-placeholder")
    sub = parser.add_subparsers(dest="command")

    p_find = sub.add_parser("find", help="Find placeholder values")
    p_find.add_argument("--file", help="Snapshot file to inspect")
    p_find.set_defaults(func=cmd_find)

    p_res = sub.add_parser("resolve", help="Resolve placeholders with provided values")
    p_res.add_argument("--file", help="Snapshot file to resolve")
    p_res.add_argument("--override", nargs="+", metavar="KEY=VALUE")
    p_res.add_argument("--override-json", dest="override_json", help="JSON object of overrides")
    p_res.add_argument("--out", help="Write resolved snapshot to file")
    p_res.set_defaults(func=cmd_resolve)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
