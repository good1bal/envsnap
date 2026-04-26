"""CLI commands for annotated diff output."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envsnap.diff import compare
from envsnap.export import from_json
from envsnap.env_diff_annotate import annotate_diff, annotated_diff_summary


def _load_snap(path: str) -> dict:
    with open(path) as fh:
        return from_json(fh.read())


def cmd_diff_annotate(ns: argparse.Namespace) -> int:
    """Compare two snapshot files and print an annotated diff."""
    try:
        snap_a = _load_snap(ns.file_a)
        snap_b = _load_snap(ns.file_b)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    notes: dict = {}
    tags: dict = {}

    if ns.notes:
        for item in ns.notes:
            if "=" not in item:
                print(f"error: invalid note format {item!r} (expected KEY=note)", file=sys.stderr)
                return 1
            k, _, v = item.partition("=")
            notes[k.strip()] = v.strip()

    if ns.tag:
        for item in ns.tag:
            if ":" not in item:
                print(f"error: invalid tag format {item!r} (expected KEY:tag)", file=sys.stderr)
                return 1
            k, _, t = item.partition(":")
            tags.setdefault(k.strip(), []).append(t.strip())

    result = compare(snap_a, snap_b)
    ad = annotate_diff(result, notes=notes, tags=tags)

    if ns.json:
        rows = [
            {
                "key": e.key,
                "status": e.status,
                "old_value": e.old_value,
                "new_value": e.new_value,
                "note": e.note,
                "tags": e.tags,
            }
            for e in ad.entries
        ]
        payload = {
            "label_a": ad.label_a,
            "label_b": ad.label_b,
            "entries": rows,
        }
        print(json.dumps(payload, indent=2))
    elif ns.summary:
        print(annotated_diff_summary(ad))
    else:
        print(f"Diff: {ad.label_a} -> {ad.label_b}")
        for e in ad.entries:
            marker = {"added": "+", "removed": "-", "changed": "~", "unchanged": "="}.get(e.status, "?")
            line = f"  {marker} {e.key}"
            if e.note:
                line += f"  # {e.note}"
            if e.tags:
                line += f"  [{', '.join(e.tags)}]"
            print(line)

    return 0 if not any(e.status != "unchanged" for e in ad.entries) else 1


def build_parser(parent: argparse._SubParsersAction = None) -> argparse.ArgumentParser:
    desc = "Show annotated diff between two snapshots"
    if parent is not None:
        p = parent.add_parser("diff-annotate", help=desc)
    else:
        p = argparse.ArgumentParser(prog="envsnap diff-annotate", description=desc)
    p.add_argument("file_a", help="First snapshot file")
    p.add_argument("file_b", help="Second snapshot file")
    p.add_argument("--notes", nargs="*", metavar="KEY=note", default=[], help="Attach notes to keys")
    p.add_argument("--tag", nargs="*", metavar="KEY:tag", default=[], help="Attach tags to keys")
    p.add_argument("--json", action="store_true", help="Output as JSON")
    p.add_argument("--summary", action="store_true", help="Print one-line summary only")
    p.set_defaults(func=cmd_diff_annotate)
    return p


def main(argv: List[str] = None) -> None:
    parser = build_parser()
    ns = parser.parse_args(argv)
    sys.exit(cmd_diff_annotate(ns))


if __name__ == "__main__":  # pragma: no cover
    main()
