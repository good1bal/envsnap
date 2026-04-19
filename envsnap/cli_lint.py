"""CLI commands for env lint."""
from __future__ import annotations
import argparse
import json
import sys
from envsnap.env_lint import lint_snapshot, lint_summary
from envsnap.snapshot import load


def cmd_lint(args: argparse.Namespace) -> None:
    if args.file:
        snap = load(args.file)
    else:
        from envsnap.snapshot import capture
        snap = capture()

    forbidden = args.forbidden or []
    max_len = args.max_value_length or 0

    result = lint_snapshot(
        snap,
        allow_lowercase=args.allow_lowercase,
        max_value_length=max_len,
        forbidden_patterns=forbidden if forbidden else None,
    )

    if args.json:
        output = [
            {"key": i.key, "message": i.message, "severity": i.severity}
            for i in result.issues
        ]
        print(json.dumps(output, indent=2))
    else:
        print(lint_summary(result))

    if not result.passed:
        sys.exit(1)


def build_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    desc = "Lint environment variable keys and values"
    if parent:
        p = parent.add_parser("lint", help=desc)
    else:
        p = argparse.ArgumentParser(prog="envsnap-lint", description=desc)

    p.add_argument("--file", metavar="PATH", help="Snapshot file to lint")
    p.add_argument(
        "--allow-lowercase", action="store_true",
        help="Do not warn on lowercase keys"
    )
    p.add_argument(
        "--max-value-length", type=int, metavar="N",
        help="Warn when a value exceeds N characters"
    )
    p.add_argument(
        "--forbidden", nargs="+", metavar="PATTERN",
        help="Regex patterns that must not appear in values"
    )
    p.add_argument("--json", action="store_true", help="Output issues as JSON")
    p.set_defaults(func=cmd_lint)
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
