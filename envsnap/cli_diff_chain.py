"""CLI commands for chained snapshot diffs."""
import argparse
import json
from envsnap.env_diff_chain import build_chain, chain_summary
from envsnap.export import from_json


def cmd_chain(args):
    snapshots = []
    for path in args.files:
        try:
            with open(path) as f:
                data = json.load(f)
            snapshots.append(data)
        except (OSError, json.JSONDecodeError) as e:
            print(f"Error loading {path}: {e}")
            raise SystemExit(1)

    if len(snapshots) < 2:
        print("At least 2 snapshot files are required.")
        raise SystemExit(1)

    chain = build_chain(snapshots)

    if args.summary:
        print(chain_summary(chain))
        return

    for link in chain.links:
        print(f"\n[{link.index}] {link.label_from} -> {link.label_to}")
        if link.result.added:
            for k, v in link.result.added.items():
                print(f"  + {k}={v}")
        if link.result.removed:
            for k, v in link.result.removed.items():
                print(f"  - {k}={v}")
        if link.result.changed:
            for k, (old, new) in link.result.changed.items():
                print(f"  ~ {k}: {old!r} -> {new!r}")
        if not (link.result.added or link.result.removed or link.result.changed):
            print("  (no changes)")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="envsnap chain",
        description="Diff a chain of snapshots in order.",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Snapshot JSON files in chronological order.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a compact summary instead of full diff.",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    cmd_chain(args)


if __name__ == "__main__":
    main()
