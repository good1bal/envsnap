"""CLI commands for snapshot validation."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from envsnap.snapshot import load, capture
from envsnap.validate import validate, validation_summary
from envsnap.schema import load_schema, save_schema, schema_from_snapshot


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate a snapshot file against a schema."""
    snap = load(args.snapshot)
    schema = load_schema(args.schema)
    result = validate(snap, **schema)
    print(validation_summary(result))
    return 0 if result.valid else 1


def cmd_validate_env(args: argparse.Namespace) -> int:
    """Capture current env and validate against a schema."""
    snap = capture()
    schema = load_schema(args.schema)
    result = validate(snap, **schema)
    print(validation_summary(result))
    return 0 if result.valid else 1


def cmd_derive_schema(args: argparse.Namespace) -> int:
    """Derive a schema from an existing snapshot (all present keys become required)."""
    snap = load(args.snapshot)
    schema = schema_from_snapshot(snap)
    out = args.output or (Path(args.snapshot).stem + ".schema.json")
    save_schema(out, required=schema.get("required"))
    print(f"Schema written to {out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="envsnap-validate",
                                     description="Validate environment snapshots.")
    sub = parser.add_subparsers(dest="command")

    p_val = sub.add_parser("file", help="Validate a snapshot file against a schema.")
    p_val.add_argument("snapshot", help="Path to snapshot JSON file.")
    p_val.add_argument("schema", help="Path to schema JSON file.")
    p_val.set_defaults(func=cmd_validate)

    p_env = sub.add_parser("env", help="Validate current environment against a schema.")
    p_env.add_argument("schema", help="Path to schema JSON file.")
    p_env.set_defaults(func=cmd_validate_env)

    p_derive = sub.add_parser("derive", help="Derive schema from snapshot.")
    p_derive.add_argument("snapshot", help="Path to snapshot JSON file.")
    p_derive.add_argument("--output", "-o", default=None, help="Output schema file path.")
    p_derive.set_defaults(func=cmd_derive_schema)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
