"""CLI commands for grouping environment variables."""
from __future__ import annotations
import argparse
import json
import sys

from envsnap.snapshot import capture
from envsnap.env_group import group_by_prefix, group_by_mapping, group_summary


def cmd_group(ns: argparse.Namespace) -> None:
    snapshot = capture(label=getattr(ns, "label", "cli"))

    prefixes = ns.prefix or []
    groups = group_by_prefix(snapshot, prefixes, other_label=ns.other or "other")

    if ns.format == "json":
        out = {name: g.keys for name, g in groups.items()}
        print(json.dumps(out, indent=2))
    else:
        print(group_summary(groups))


def cmd_group_map(ns: argparse.Namespace) -> None:
    """Group using an explicit JSON mapping file."""
    try:
        with open(ns.mapping_file) as f:
            mapping: dict = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    snapshot = capture(label=getattr(ns, "label", "cli"))
    groups = group_by_mapping(snapshot, mapping, other_label=ns.other or "other")

    if ns.format == "json":
        out = {name: g.keys for name, g in groups.items()}
        print(json.dumps(out, indent=2))
    else:
        print(group_summary(groups))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="envsnap-group", description="Group env vars")
    parser.add_argument("--label", default="cli", help="Snapshot label")
    parser.add_argument("--other", default="other", help="Label for ungrouped keys")
    parser.add_argument("--format", choices=["text", "json"], default="text")

    sub = parser.add_subparsers(dest="command")

    p_prefix = sub.add_parser("prefix", help="Group by prefix")
    p_prefix.add_argument("prefix", nargs="*", help="Prefixes to group by")
    p_prefix.set_defaults(func=cmd_group)

    p_map = sub.add_parser("map", help="Group by mapping file")
    p_map.add_argument("mapping_file", help="Path to JSON mapping file")
    p_map.set_defaults(func=cmd_group_map)

    return parser


def main() -> None:
    parser = build_parser()
    ns = parser.parse_args()
    if not hasattr(ns, "func"):
        parser.print_help()
        sys.exit(0)
    ns.func(ns)


if __name__ == "__main__":
    main()
