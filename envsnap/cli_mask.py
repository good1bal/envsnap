"""CLI commands for masking environment variable values."""
from __future__ import annotations
import argparse
import json
from envsnap.snapshot import load
from envsnap.env_mask import mask_snapshot, mask_summary
from envsnap.export import to_json, to_dotenv


def cmd_mask(args: argparse.Namespace) -> None:
    snap = load(args.file)
    keys = args.keys or []
    result = mask_snapshot(
        snap["env"],
        keys=keys if keys else None,
        placeholder=args.placeholder,
        auto_detect=not args.no_auto,
    )
    if args.summary:
        print(mask_summary(result))
        return
    masked_snap = dict(snap)
    masked_snap["env"] = result.masked
    if args.format == "dotenv":
        print(to_dotenv(masked_snap))
    else:
        print(to_json(masked_snap))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="envsnap mask", description="Mask sensitive env values")
    p.add_argument("file", help="Snapshot file to mask")
    p.add_argument("--keys", nargs="+", metavar="KEY", help="Explicit keys to mask")
    p.add_argument("--placeholder", default="***", help="Replacement string (default: ***)")
    p.add_argument("--no-auto", action="store_true", help="Disable auto-detection of sensitive keys")
    p.add_argument("--summary", action="store_true", help="Print summary only")
    p.add_argument("--format", choices=["json", "dotenv"], default="json", help="Output format")
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    cmd_mask(args)


if __name__ == "__main__":
    main()
