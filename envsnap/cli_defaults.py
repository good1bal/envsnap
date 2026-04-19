"""CLI commands for applying environment defaults."""
from __future__ import annotations
import argparse
import json
import os

from envsnap.env_defaults import apply_defaults, missing_keys, defaults_summary
from envsnap.snapshot import load, save


def cmd_apply(args: argparse.Namespace) -> None:
    """Apply defaults from a JSON file or key=value pairs to a snapshot."""
    snap = load(args.snapshot)

    defaults: dict[str, str] = {}
    if args.defaults_file:
        with open(args.defaults_file) as fh:
            defaults.update(json.load(fh))
    for pair in args.set or []:
        key, _, value = pair.partition("=")
        defaults[key.strip()] = value

    result = apply_defaults(snap, defaults, overwrite=args.overwrite)

    if args.output:
        save(result.snapshot, args.output)
    else:
        save(result.snapshot, args.snapshot)

    print(defaults_summary(result))


def cmd_missing(args: argparse.Namespace) -> None:
    """List keys from a defaults file that are absent in the snapshot."""
    snap = load(args.snapshot)
    with open(args.defaults_file) as fh:
        defaults = json.load(fh)

    absent = missing_keys(snap, defaults)
    if absent:
        print(f"{len(absent)} missing key(s):")
        for k in absent:
            print(f"  - {k}")
    else:
        print("All default keys are present in the snapshot.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envsnap-defaults",
        description="Apply default values to an envsnap snapshot.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_apply = sub.add_parser("apply", help="Apply defaults to a snapshot file.")
    p_apply.add_argument("snapshot", help="Path to snapshot JSON file.")
    p_apply.add_argument("--defaults-file", metavar="FILE", help="JSON file of defaults.")
    p_apply.add_argument("--set", nargs="*", metavar="KEY=VALUE", help="Inline defaults.")
    p_apply.add_argument("--overwrite", action="store_true", help="Overwrite existing keys.")
    p_apply.add_argument("--output", metavar="FILE", help="Write result to a new file.")
    p_apply.set_defaults(func=cmd_apply)

    p_miss = sub.add_parser("missing", help="Show which default keys are absent.")
    p_miss.add_argument("snapshot", help="Path to snapshot JSON file.")
    p_miss.add_argument("defaults_file", metavar="DEFAULTS", help="JSON file of defaults.")
    p_miss.set_defaults(func=cmd_missing)

    return parser


def main() -> None:  # pragma: no cover
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()
