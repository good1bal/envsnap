"""CLI commands for the env-protect feature."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from envsnap.env_protect import (
    check_protected,
    load_protected,
    protect_keys,
    protect_summary,
    save_protected,
)
from envsnap.export import from_json


def _store(args: argparse.Namespace) -> Optional[Path]:
    return Path(args.store) if getattr(args, "store", None) else None


def cmd_protect(args: argparse.Namespace) -> None:
    """Mark keys as protected in the store."""
    env = from_json(Path(args.file).read_text()) if args.file else {}
    result = protect_keys(env, args.keys, _store(args))
    if args.json:
        print(json.dumps({"protected": result.protected}))
    else:
        print(protect_summary(result))


def cmd_unprotect(args: argparse.Namespace) -> None:
    """Remove keys from the protected set."""
    store = _store(args)
    current = load_protected(store)
    remaining = [k for k in current if k not in args.keys]
    save_protected(remaining, store)
    print(f"Removed {len(current) - len(remaining)} key(s) from protected set.")


def cmd_list(args: argparse.Namespace) -> None:
    """List all currently protected keys."""
    keys = load_protected(_store(args))
    if args.json:
        print(json.dumps(keys))
    else:
        if keys:
            for k in keys:
                print(f"  {k}")
        else:
            print("(no protected keys)")


def cmd_check(args: argparse.Namespace) -> None:
    """Check an updated snapshot for protected-key violations."""
    original = from_json(Path(args.original).read_text())
    updated = from_json(Path(args.updated).read_text())
    result = check_protected(original, updated, _store(args))
    if args.json:
        print(json.dumps({
            "violations": [{"key": v.key, "reason": v.reason} for v in result.violations]
        }))
    else:
        print(protect_summary(result))
    if result.violations:
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="envsnap protect")
    parser.add_argument("--store", default=None, help="Path to .envsnap store directory")
    sub = parser.add_subparsers(dest="cmd")

    p = sub.add_parser("add", help="Mark keys as protected")
    p.add_argument("keys", nargs="+")
    p.add_argument("--file", default=None)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_protect)

    u = sub.add_parser("remove", help="Unprotect keys")
    u.add_argument("keys", nargs="+")
    u.set_defaults(func=cmd_unprotect)

    ls = sub.add_parser("list", help="List protected keys")
    ls.add_argument("--json", action="store_true")
    ls.set_defaults(func=cmd_list)

    ck = sub.add_parser("check", help="Check snapshot for violations")
    ck.add_argument("original")
    ck.add_argument("updated")
    ck.add_argument("--json", action="store_true")
    ck.set_defaults(func=cmd_check)

    return parser


def main() -> None:  # pragma: no cover
    parser = build_parser()
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()
