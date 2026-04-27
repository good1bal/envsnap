"""CLI commands for env-diff scoring."""
from __future__ import annotations

import argparse
import json
import sys

from envsnap.export import from_json
from envsnap.env_diff_score import score, score_summary


def cmd_score(args: argparse.Namespace) -> None:
    """Compare two snapshot files and print a similarity score."""
    try:
        with open(args.file_a) as fh:
            snap_a = from_json(fh.read())
        with open(args.file_b) as fh:
            snap_b = from_json(fh.read())
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    ds = score(snap_a, snap_b)

    if args.json:
        output = {
            "label_a": ds.label_a,
            "label_b": ds.label_b,
            "total_keys": ds.total_keys,
            "added": ds.added,
            "removed": ds.removed,
            "changed": ds.changed,
            "unchanged": ds.unchanged,
            "similarity": ds.similarity,
            "divergence": ds.divergence,
            "breakdown": ds.breakdown,
        }
        print(json.dumps(output, indent=2))
    else:
        print(score_summary(ds))
        if args.verbose:
            print(f"  total keys : {ds.total_keys}")
            print(f"  added      : {ds.added}")
            print(f"  removed    : {ds.removed}")
            print(f"  changed    : {ds.changed}")
            print(f"  unchanged  : {ds.unchanged}")
            for k, v in ds.breakdown.items():
                print(f"  {k:<20}: {v:.1%}")

    if args.fail_below is not None and ds.similarity < args.fail_below:
        sys.exit(2)


def build_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    desc = "Score the similarity/divergence between two environment snapshots."
    if parent is not None:
        p = parent.add_parser("score", help=desc)
    else:
        p = argparse.ArgumentParser(prog="envsnap-score", description=desc)

    p.add_argument("file_a", help="First snapshot JSON file")
    p.add_argument("file_b", help="Second snapshot JSON file")
    p.add_argument("--json", action="store_true", help="Output as JSON")
    p.add_argument("-v", "--verbose", action="store_true", help="Show full breakdown")
    p.add_argument(
        "--fail-below",
        type=float,
        metavar="THRESHOLD",
        default=None,
        help="Exit with code 2 if similarity is below THRESHOLD (0.0-1.0)",
    )
    p.set_defaults(func=cmd_score)
    return p


def main() -> None:  # pragma: no cover
    parser = build_parser()
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()
