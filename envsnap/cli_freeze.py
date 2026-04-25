"""CLI commands for freeze/unfreeze/check of environment keys."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envsnap.env_freeze import (
    freeze_keys,
    unfreeze_keys,
    check_freeze,
    freeze_summary,
    load_frozen,
)
from envsnap.snapshot import load


def cmd_freeze(args: argparse.Namespace) -> None:
    """Freeze keys from a snapshot file."""
    snapshot = load(args.file)
    keys: Optional[List[str]] = args.keys if args.keys else None
    result = freeze_keys(snapshot, keys=keys, store_dir=args.store)
    if args.summary:
        print(freeze_summary(result))
    else:
        for k in result.frozen_keys:
            print(f"  frozen  {k}")
        for k in result.skipped_keys:
            print(f"  skipped {k} (not in snapshot)")


def cmd_unfreeze(args: argparse.Namespace) -> None:
    """Remove keys from the freeze store."""
    removed = unfreeze_keys(args.keys, store_dir=args.store)
    if removed:
        for k in removed:
            print(f"  unfrozen {k}")
    else:
        print("No matching frozen keys found.")


def cmd_check(args: argparse.Namespace) -> None:
    """Check a snapshot against frozen values; exit 1 if violations exist."""
    snapshot = load(args.file)
    violations = check_freeze(snapshot, store_dir=args.store)
    if not violations:
        print("OK — no freeze violations.")
        sys.exit(0)
    for v in violations:
        print(f"  VIOLATION  {v.key}: {v.reason}")
    sys.exit(1)


def cmd_list(args: argparse.Namespace) -> None:
    """List all currently frozen keys."""
    frozen = load_frozen(args.store)
    if not frozen:
        print("No keys are frozen.")
        return
    for key, value in sorted(frozen.items()):
        display = value if not args.show_values else value
        masked = "***" if not args.show_values else display
        print(f"  {key} = {masked}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="envsnap freeze", description="Freeze env keys")
    parser.add_argument("--store", default=".envsnap", help="Storage directory")
    sub = parser.add_subparsers(dest="command", required=True)

    p_freeze = sub.add_parser("freeze", help="Freeze keys from snapshot")
    p_freeze.add_argument("file", help="Snapshot file")
    p_freeze.add_argument("keys", nargs="*", help="Keys to freeze (default: all)")
    p_freeze.add_argument("--summary", action="store_true")
    p_freeze.set_defaults(func=cmd_freeze)

    p_unfreeze = sub.add_parser("unfreeze", help="Unfreeze specific keys")
    p_unfreeze.add_argument("keys", nargs="+", help="Keys to unfreeze")
    p_unfreeze.set_defaults(func=cmd_unfreeze)

    p_check = sub.add_parser("check", help="Check snapshot against frozen values")
    p_check.add_argument("file", help="Snapshot file")
    p_check.set_defaults(func=cmd_check)

    p_list = sub.add_parser("list", help="List frozen keys")
    p_list.add_argument("--show-values", action="store_true")
    p_list.set_defaults(func=cmd_list)

    return parser


def main(argv=None) -> None:  # pragma: no cover
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()
