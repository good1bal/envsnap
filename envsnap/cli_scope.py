"""CLI commands for env scope management."""
from __future__ import annotations
import argparse
import json
from envsnap.env_scope import assign_scope, filter_by_scope, scope_summary, remove_scope


def cmd_assign(args: argparse.Namespace) -> None:
    with open(args.file) as f:
        snapshot = json.load(f)
    keys = args.keys
    updated = assign_scope(snapshot, keys, args.scope)
    out = args.out or args.file
    with open(out, "w") as f:
        json.dump(updated, f, indent=2)
    print(f"Assigned scope '{args.scope}' to {len(keys)} key(s) -> {out}")


def cmd_filter(args: argparse.Namespace) -> None:
    with open(args.file) as f:
        snapshot = json.load(f)
    result = filter_by_scope(snapshot, args.scope)
    if not result:
        print(f"No keys found for scope '{args.scope}'.")
        return
    for k, v in sorted(result.items()):
        print(f"{k}={v}")


def cmd_summary(args: argparse.Namespace) -> None:
    with open(args.file) as f:
        snapshot = json.load(f)
    summary = scope_summary(snapshot)
    if not summary:
        print("No scopes defined.")
        return
    for scope, keys in sorted(summary.items()):
        print(f"[{scope}] ({len(keys)} keys)")
        for k in sorted(keys):
            print(f"  {k}")


def cmd_remove(args: argparse.Namespace) -> None:
    with open(args.file) as f:
        snapshot = json.load(f)
    updated = snapshot
    for k in args.keys:
        updated = remove_scope(updated, k)
    out = args.out or args.file
    with open(out, "w") as f:
        json.dump(updated, f, indent=2)
    print(f"Removed scope from {len(args.keys)} key(s) -> {out}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="envsnap scope", description="Manage env var scopes")
    sub = p.add_subparsers(dest="command")

    pa = sub.add_parser("assign", help="Assign a scope to keys")
    pa.add_argument("file")
    pa.add_argument("--scope", required=True)
    pa.add_argument("--keys", nargs="+", required=True)
    pa.add_argument("--out")
    pa.set_defaults(func=cmd_assign)

    pf = sub.add_parser("filter", help="List keys for a scope")
    pf.add_argument("file")
    pf.add_argument("--scope", required=True)
    pf.set_defaults(func=cmd_filter)

    ps = sub.add_parser("summary", help="Show all scopes")
    ps.add_argument("file")
    ps.set_defaults(func=cmd_summary)

    pr = sub.add_parser("remove", help="Remove scope from keys")
    pr.add_argument("file")
    pr.add_argument("--keys", nargs="+", required=True)
    pr.add_argument("--out")
    pr.set_defaults(func=cmd_remove)

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
