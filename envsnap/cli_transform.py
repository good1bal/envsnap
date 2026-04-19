"""CLI commands for env-transform feature."""
from __future__ import annotations
import argparse
import json
import os
from envsnap.env_transform import (
    uppercase_values,
    lowercase_values,
    strip_values,
    apply_transform,
    transform_summary,
)
from envsnap.snapshot import capture


_BUILTIN = {
    "upper": uppercase_values,
    "lower": lowercase_values,
    "strip": strip_values,
}


def cmd_transform(args: argparse.Namespace) -> None:
    if args.file:
        from envsnap.export import from_json
        with open(args.file) as fh:
            snap = from_json(fh.read())["env"]
    else:
        snap = capture()["env"]

    keys = args.keys if args.keys else None
    op = args.operation

    if op not in _BUILTIN:
        print(f"Unknown operation '{op}'. Choose from: {', '.join(_BUILTIN)}.")
        raise SystemExit(1)

    result = _BUILTIN[op](snap, keys=keys)

    if args.summary:
        print(transform_summary(result))
    else:
        print(json.dumps(result.transformed, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envsnap-transform",
        description="Transform environment variable values.",
    )
    p.add_argument("operation", choices=list(_BUILTIN), help="Transformation to apply")
    p.add_argument("--file", metavar="PATH", help="Load snapshot from JSON file")
    p.add_argument("--keys", nargs="+", metavar="KEY", help="Limit to specific keys")
    p.add_argument("--summary", action="store_true", help="Print summary instead of JSON")
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    cmd_transform(args)


if __name__ == "__main__":
    main()
