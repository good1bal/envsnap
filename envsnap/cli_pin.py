"""CLI commands for managing pinned environment variable values."""
from __future__ import annotations

import argparse
import os

from envsnap.pin import check_pins, load_pins, pin_key, save_pins, unpin_key


def cmd_pin(args: argparse.Namespace) -> None:
    value = os.environ.get(args.key) if args.value is None else args.value
    if value is None:
        print(f"Error: {args.key!r} not found in environment and no value provided.")
        return
    pin_key(args.key, value, args.dir)
    print(f"Pinned {args.key}={value!r}")


def cmd_unpin(args: argparse.Namespace) -> None:
    unpin_key(args.key, args.dir)
    print(f"Unpinned {args.key}")


def cmd_list(args: argparse.Namespace) -> None:
    pins = load_pins(args.dir)
    if not pins:
        print("No pins defined.")
        return
    for key, value in sorted(pins.items()):
        print(f"  {key}={value!r}")


def cmd_check(args: argparse.Namespace) -> None:
    env = dict(os.environ)
    violations = check_pins(env, args.dir)
    if not violations:
        print("All pins match.")
    else:
        for v in violations:
            print(f"  FAIL  {v}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="envsnap pin", description="Manage pinned env values")
    parser.add_argument("--dir", default=".", help="Directory for pin file")
    sub = parser.add_subparsers(dest="subcmd")

    p = sub.add_parser("set", help="Pin a key to a value")
    p.add_argument("key")
    p.add_argument("value", nargs="?", default=None)
    p.set_defaults(func=cmd_pin)

    u = sub.add_parser("unset", help="Remove a pin")
    u.add_argument("key")
    u.set_defaults(func=cmd_unpin)

    sub.add_parser("list", help="List all pins").set_defaults(func=cmd_list)
    sub.add_parser("check", help="Check current env against pins").set_defaults(func=cmd_check)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
