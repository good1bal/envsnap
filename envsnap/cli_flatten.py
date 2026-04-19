"""CLI commands for flattening nested env structures."""
from __future__ import annotations
import argparse
import json
import sys
from envsnap.env_flatten import flatten, unflatten, flatten_summary


def cmd_flatten(args: argparse.Namespace) -> None:
    try:
        with open(args.file) as fh:
            data = json.load(fh)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON: {exc}", file=sys.stderr)
        sys.exit(1)

    sep = args.separator or "__"
    flat = flatten(data, separator=sep)

    if args.summary:
        print(flatten_summary(data, flat))
        return

    print(json.dumps(flat, indent=2, sort_keys=True))


def cmd_unflatten(args: argparse.Namespace) -> None:
    try:
        with open(args.file) as fh:
            data = json.load(fh)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON: {exc}", file=sys.stderr)
        sys.exit(1)

    sep = args.separator or "__"
    nested = unflatten(data, separator=sep)
    print(json.dumps(nested, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="envsnap-flatten", description="Flatten or unflatten env JSON")
    sub = parser.add_subparsers(dest="command")

    p_flat = sub.add_parser("flatten", help="Flatten nested JSON to flat key=value")
    p_flat.add_argument("file", help="Input JSON file")
    p_flat.add_argument("--separator", default="__", help="Key separator (default: __)")
    p_flat.add_argument("--summary", action="store_true", help="Print summary only")
    p_flat.set_defaults(func=cmd_flatten)

    p_un = sub.add_parser("unflatten", help="Unflatten flat keys back to nested JSON")
    p_un.add_argument("file", help="Input JSON file")
    p_un.add_argument("--separator", default="__", help="Key separator (default: __)")
    p_un.set_defaults(func=cmd_unflatten)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
