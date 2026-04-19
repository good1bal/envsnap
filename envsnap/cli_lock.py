"""CLI commands for env lock management."""
from __future__ import annotations

import argparse
import os
import sys

from envsnap.snapshot import capture
from envsnap.env_lock import (
    check_lock,
    load_lock,
    lock_keys,
    lock_summary,
    save_lock,
)

DEFAULT_LOCK_FILE = ".envlock.json"


def cmd_lock(ns: argparse.Namespace) -> None:
    """Lock specified keys from the current environment."""
    snap = capture()
    keys = ns.keys
    locked = lock_keys(snap, keys)
    missing = [k for k in keys if k not in locked]
    if missing:
        print(f"Warning: keys not found in environment: {', '.join(missing)}", file=sys.stderr)
    path = ns.file or DEFAULT_LOCK_FILE
    existing = load_lock(path)
    existing.update(locked)
    save_lock(existing, path)
    print(f"Locked {len(locked)} key(s) to {path}.")


def cmd_check(ns: argparse.Namespace) -> None:
    """Check current environment against lock file."""
    path = ns.file or DEFAULT_LOCK_FILE
    locked = load_lock(path)
    if not locked:
        print("No lock file found or lock is empty.")
        sys.exit(0)
    snap = capture()
    violations = check_lock(snap, locked)
    print(lock_summary(violations))
    if violations:
        sys.exit(1)


def cmd_show(ns: argparse.Namespace) -> None:
    """Show current lock file contents."""
    import json
    path = ns.file or DEFAULT_LOCK_FILE
    locked = load_lock(path)
    if not locked:
        print("Lock file is empty or does not exist.")
        return
    print(json.dumps(locked, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="envsnap lock", description="Manage env key locks")
    parser.add_argument("--file", default=None, help="Path to lock file")
    sub = parser.add_subparsers(dest="command")

    p_lock = sub.add_parser("add", help="Lock keys from current env")
    p_lock.add_argument("keys", nargs="+", help="Keys to lock")
    p_lock.set_defaults(func=cmd_lock)

    p_check = sub.add_parser("check", help="Check env against lock")
    p_check.set_defaults(func=cmd_check)

    p_show = sub.add_parser("show", help="Show locked keys")
    p_show.set_defaults(func=cmd_show)

    return parser


def main() -> None:
    parser = build_parser()
    ns = parser.parse_args()
    if not hasattr(ns, "func"):
        parser.print_help()
        sys.exit(1)
    ns.func(ns)


if __name__ == "__main__":
    main()
