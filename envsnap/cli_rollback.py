"""CLI commands for env rollback."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from envsnap.export import from_json
from envsnap.env_rollback import rollback, rollback_summary


def cmd_rollback(ns: argparse.Namespace) -> None:
    """Revert current snapshot to a target snapshot."""
    try:
        with open(ns.current) as fh:
            current = from_json(fh.read())
        with open(ns.target) as fh:
            target = from_json(fh.read())
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    keys: Optional[List[str]] = ns.keys if ns.keys else None
    result = rollback(current, target, keys=keys)

    if ns.json:
        out = {
            "reverted": result.reverted,
            "keys_restored": result.keys_restored,
            "keys_removed": result.keys_removed,
            "keys_unchanged": result.keys_unchanged,
        }
        print(json.dumps(out, indent=2, sort_keys=True))
    elif ns.summary:
        print(rollback_summary(result))
    else:
        for key in result.keys_restored:
            print(f"~ {key}")
        for key in result.keys_removed:
            print(f"- {key}")

    if ns.output:
        from envsnap.export import to_json
        new_snap = dict(current)
        new_snap["env"] = result.reverted
        with open(ns.output, "w") as fh:
            fh.write(to_json(new_snap))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="envsnap rollback", description="Rollback env to a previous snapshot")
    p.add_argument("current", help="Path to current snapshot JSON")
    p.add_argument("target", help="Path to target (older) snapshot JSON")
    p.add_argument("--keys", nargs="+", metavar="KEY", help="Limit rollback to specific keys")
    p.add_argument("--output", metavar="FILE", help="Write reverted snapshot to file")
    p.add_argument("--json", action="store_true", help="Output as JSON")
    p.add_argument("--summary", action="store_true", help="Print summary only")
    return p


def main() -> None:  # pragma: no cover
    parser = build_parser()
    ns = parser.parse_args()
    cmd_rollback(ns)


if __name__ == "__main__":  # pragma: no cover
    main()
