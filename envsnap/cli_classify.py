"""CLI commands for env-classify feature."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from envsnap.env_classify import classify, classify_summary
from envsnap.export import from_json
from envsnap.snapshot import capture


def _load_env(path: Optional[str]):
    if path:
        with open(path) as fh:
            snap = from_json(fh.read())
        return snap["env"]
    return capture()["env"]


def cmd_classify(args: argparse.Namespace) -> int:
    """Classify keys from the live environment or a snapshot file."""
    env = _load_env(getattr(args, "file", None))

    custom_rules = None
    if getattr(args, "rules", None):
        # Expect repeated  PATTERN:CATEGORY  strings
        custom_rules = []
        for token in args.rules:
            if ":" not in token:
                print(f"Invalid rule '{token}' — expected PATTERN:CATEGORY", file=sys.stderr)
                return 2
            pattern, category = token.split(":", 1)
            custom_rules.append((pattern.strip(), category.strip()))

    result = classify(env, rules=custom_rules)

    if getattr(args, "json", False):
        payload = {cat: sorted(keys) for cat, keys in sorted(result.categories.items())}
        print(json.dumps(payload, indent=2))
    elif getattr(args, "summary", False):
        print(classify_summary(result))
    else:
        for key, cat in sorted(result.key_map.items()):
            print(f"{key}={cat}")

    return 0


def build_parser(parser: Optional[argparse.ArgumentParser] = None) -> argparse.ArgumentParser:
    if parser is None:
        parser = argparse.ArgumentParser(
            prog="envsnap classify",
            description="Classify environment variable keys into semantic categories.",
        )
    parser.add_argument("--file", metavar="PATH", help="Snapshot JSON file (default: live env)")
    parser.add_argument(
        "--rules",
        nargs="+",
        metavar="PATTERN:CATEGORY",
        help="Custom classification rules (overrides defaults)",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--summary", action="store_true", help="Print summary only")
    return parser


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    sys.exit(cmd_classify(args))


if __name__ == "__main__":
    main()
