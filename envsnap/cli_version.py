"""CLI commands for snapshot versioning."""
from __future__ import annotations

import argparse
import json
import os
import sys

from envsnap.env_version import add_version, load_versions, save_versions, version_summary
from envsnap.snapshot import capture

_DEFAULT_STORE = ".envsnap_versions.json"


def cmd_add(args: argparse.Namespace) -> None:
    store = load_versions(args.store)
    env = capture(label=args.label)
    entry = add_version(store, label=args.label, env=env["env"])
    save_versions(args.store, store)
    print(f"Recorded version v{entry.version} ({args.label}) checksum={entry.checksum[:8]}")


def cmd_list(args: argparse.Namespace) -> None:
    store = load_versions(args.store)
    if args.json:
        out = [
            {"version": e.version, "label": e.label, "checksum": e.checksum}
            for e in store.entries
        ]
        print(json.dumps(out, indent=2))
    else:
        print(version_summary(store))


def cmd_show(args: argparse.Namespace) -> None:
    store = load_versions(args.store)
    entry = store.get(args.version)
    if entry is None:
        print(f"Version {args.version} not found.", file=sys.stderr)
        sys.exit(1)
    if args.json:
        print(json.dumps({"version": entry.version, "label": entry.label, "env": entry.env}, indent=2))
    else:
        print(f"v{entry.version}  {entry.label}  [{entry.checksum[:8]}]")
        for k, v in sorted(entry.env.items()):
            print(f"  {k}={v}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="envsnap version", description="Manage snapshot versions")
    p.add_argument("--store", default=_DEFAULT_STORE)
    sub = p.add_subparsers(dest="cmd")

    add_p = sub.add_parser("add", help="Record current environment as a new version")
    add_p.add_argument("--label", default="snapshot")
    add_p.set_defaults(func=cmd_add)

    list_p = sub.add_parser("list", help="List all versions")
    list_p.add_argument("--json", action="store_true")
    list_p.set_defaults(func=cmd_list)

    show_p = sub.add_parser("show", help="Show a specific version")
    show_p.add_argument("version", type=int)
    show_p.add_argument("--json", action="store_true")
    show_p.set_defaults(func=cmd_show)

    return p


def main() -> None:  # pragma: no cover
    parser = build_parser()
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()
