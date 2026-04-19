"""CLI commands for extracting keys from a snapshot."""
from __future__ import annotations
import argparse
import json
import sys
from typing import List

from envsnap.env_extract import extract_keys, extract_summary
from envsnap.export import from_json, to_json


def cmd_extract(args: argparse.Namespace) -> None:
    try:
        with open(args.file) as fh:
            snap = from_json(fh.read())
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    keys: List[str] = args.keys
    result = extract_keys(
        snap["env"],
        keys,
        default=args.default,
        skip_missing=not args.fill_missing,
    )

    if args.summary:
        print(extract_summary(result))
        return

    output_snap = dict(snap)
    output_snap["env"] = result.env

    if args.output:
        with open(args.output, "w") as fh:
            fh.write(to_json(output_snap))
        print(f"Wrote {len(result.extracted)} key(s) to {args.output}")
    else:
        print(to_json(output_snap))

    if result.missing:
        print(
            f"Warning: {len(result.missing)} key(s) not found: "
            + ", ".join(sorted(result.missing)),
            file=sys.stderr,
        )


def build_parser(parser: argparse.ArgumentParser = None) -> argparse.ArgumentParser:
    if parser is None:
        parser = argparse.ArgumentParser(description="Extract keys from a snapshot")
    parser.add_argument("file", help="Path to snapshot JSON file")
    parser.add_argument("keys", nargs="+", help="Keys to extract")
    parser.add_argument("-o", "--output", help="Write result to file")
    parser.add_argument("--fill-missing", action="store_true", help="Include missing keys with default value")
    parser.add_argument("--default", default="", help="Default value for missing keys (requires --fill-missing)")
    parser.add_argument("--summary", action="store_true", help="Print summary only")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    cmd_extract(args)


if __name__ == "__main__":
    main()
