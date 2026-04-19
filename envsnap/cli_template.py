"""CLI commands for env template generation and validation."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envsnap.env_template import (
    build_template,
    apply_template,
    template_diff,
    template_summary,
    TemplateMissingKey,
)
from envsnap.snapshot import load


def cmd_generate(args: argparse.Namespace) -> None:
    """Generate a template JSON from a snapshot file."""
    snap = load(args.snapshot)
    tmpl = build_template(snap)
    out = json.dumps(tmpl, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(out)
        print(f"Template written to {args.output}")
    else:
        print(out)


def cmd_check(args: argparse.Namespace) -> None:
    """Check a snapshot against a template file."""
    tmpl = json.loads(Path(args.template).read_text())
    snap = load(args.snapshot)
    diff = template_diff(tmpl, snap)
    print(template_summary(diff))
    if diff["missing_in_snapshot"] or diff["extra_in_snapshot"]:
        sys.exit(1)


def cmd_fill(args: argparse.Namespace) -> None:
    """Fill a template with values from a snapshot."""
    tmpl = json.loads(Path(args.template).read_text())
    snap = load(args.snapshot)
    env = snap.get("env", {})
    try:
        filled = apply_template(tmpl, env, allow_missing=args.allow_missing)
    except TemplateMissingKey as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(filled, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="envsnap template", description="Template commands")
    sub = parser.add_subparsers(dest="command")

    gen = sub.add_parser("generate", help="Generate template from snapshot")
    gen.add_argument("snapshot")
    gen.add_argument("-o", "--output", default="")
    gen.set_defaults(func=cmd_generate)

    chk = sub.add_parser("check", help="Check snapshot against template")
    chk.add_argument("template")
    chk.add_argument("snapshot")
    chk.set_defaults(func=cmd_check)

    fill = sub.add_parser("fill", help="Fill template from snapshot values")
    fill.add_argument("template")
    fill.add_argument("snapshot")
    fill.add_argument("--allow-missing", action="store_true")
    fill.set_defaults(func=cmd_fill)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
