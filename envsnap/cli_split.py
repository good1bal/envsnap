"""CLI commands for env-split feature."""
from __future__ import annotations
import argparse
import json
import sys
from envsnap.env_split import split_by_prefix, split_by_keys, split_summary
from envsnap.export import from_json, to_json


def cmd_split_prefix(args: argparse.Namespace) -> None:
    with open(args.file) as f:
        snap = from_json(f.read())
    env = snap.get("vars", snap)
    result = split_by_prefix(
        env,
        prefixes=args.prefixes,
        strip_prefix=args.strip_prefix,
        label=args.file,
    )
    if args.summary:
        print(split_summary(result))
        return
    output = {name: part for name, part in result.parts.items()}
    if args.include_remainder and result.remainder:
        output["__remainder__"] = result.remainder
    print(json.dumps(output, indent=2, sort_keys=True))


def cmd_split_groups(args: argparse.Namespace) -> None:
    with open(args.file) as f:
        snap = from_json(f.read())
    env = snap.get("vars", snap)
    with open(args.groups_file) as gf:
        groups = json.load(gf)
    result = split_by_keys(env, groups, label=args.file)
    if args.summary:
        print(split_summary(result))
        return
    output = dict(result.parts)
    if args.include_remainder and result.remainder:
        output["__remainder__"] = result.remainder
    print(json.dumps(output, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="envsnap-split")
    sub = p.add_subparsers(dest="command")

    pp = sub.add_parser("prefix", help="Split by prefix")
    pp.add_argument("file")
    pp.add_argument("prefixes", nargs="+")
    pp.add_argument("--strip-prefix", action="store_true")
    pp.add_argument("--include-remainder", action="store_true")
    pp.add_argument("--summary", action="store_true")
    pp.set_defaults(func=cmd_split_prefix)

    gp = sub.add_parser("groups", help="Split by key groups file")
    gp.add_argument("file")
    gp.add_argument("groups_file")
    gp.add_argument("--include-remainder", action="store_true")
    gp.add_argument("--summary", action="store_true")
    gp.set_defaults(func=cmd_split_groups)

    return p


def main() -> None:
    p = build_parser()
    args = p.parse_args()
    if not args.command:
        p.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
