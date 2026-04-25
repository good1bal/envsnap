"""CLI commands for required-key checking."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envsnap.env_required import check_required, required_summary
from envsnap.export import from_json
from envsnap.snapshot import capture


def cmd_check(args: argparse.Namespace) -> None:
    """Check that required keys exist in a snapshot or the live environment."""
    if args.file:
        with open(args.file) as fh:
            snap = from_json(fh.read())
    else:
        snap = capture()

    defaults: dict = {}
    if args.defaults:
        for pair in args.defaults:
            if "=" not in pair:
                print(f"[error] invalid default '{pair}' (expected KEY=VALUE)", file=sys.stderr)
                sys.exit(2)
            k, v = pair.split("=", 1)
            defaults[k] = v

    result = check_required(
        snap,
        args.keys,
        defaults=defaults or None,
        apply_defaults=args.apply_defaults,
    )

    if args.json:
        payload = {
            "satisfied": result.satisfied,
            "present": sorted(result.present),
            "missing": sorted(result.missing),
            "defaults_applied": result.defaults_applied,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(required_summary(result))

    if not result.satisfied:
        sys.exit(1)


def build_parser(parent: argparse._SubParsersAction = None) -> argparse.ArgumentParser:  # type: ignore[assignment]
    desc = "Check that required environment variable keys are present."
    if parent is not None:
        parser = parent.add_parser("required", help=desc)
    else:
        parser = argparse.ArgumentParser(prog="envsnap-required", description=desc)

    parser.add_argument("keys", nargs="+", metavar="KEY", help="Required key names")
    parser.add_argument("-f", "--file", metavar="FILE", help="Snapshot JSON file (default: live env)")
    parser.add_argument(
        "-d",
        "--default",
        dest="defaults",
        action="append",
        metavar="KEY=VALUE",
        help="Provide a fallback value for a missing key (repeatable)",
    )
    parser.add_argument(
        "--apply-defaults",
        action="store_true",
        default=False,
        help="Treat keys with supplied defaults as satisfied",
    )
    parser.add_argument("--json", action="store_true", default=False, help="Output as JSON")
    parser.set_defaults(func=cmd_check)
    return parser


def main(argv: List[str] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()
