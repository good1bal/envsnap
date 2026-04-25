"""CLI commands for env-pivot: compare multiple snapshots in a table view."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

from envsnap.env_pivot import build_pivot, pivot_summary
from envsnap.export import from_json


def _load_snap(path: str) -> dict:
    text = Path(path).read_text()
    return from_json(text)


def cmd_pivot(ns: argparse.Namespace) -> None:
    if len(ns.files) < 2:
        print("error: at least two snapshot files required", file=sys.stderr)
        sys.exit(1)

    snapshots: dict = {}
    for fpath in ns.files:
        snap = _load_snap(fpath)
        label = snap.get("label") or Path(fpath).stem
        snapshots[label] = snap.get("env", {})

    table = build_pivot(snapshots)

    if ns.summary:
        print(pivot_summary(table))
        return

    if ns.differing_only:
        rows = table.differing_rows()
    else:
        rows = table.rows

    if ns.json:
        out = [
            {"key": r.key, "values": r.values, "uniform": r.is_uniform()}
            for r in rows
        ]
        print(json.dumps(out, indent=2))
        return

    col_w = max((len(l) for l in table.labels), default=8)
    key_w = max((len(r.key) for r in rows), default=3) if rows else 3
    header = f"{'KEY':<{key_w}}  " + "  ".join(f"{l:<{col_w}}" for l in table.labels)
    print(header)
    print("-" * len(header))
    for row in rows:
        vals = "  ".join(
            f"{(row.values[l] or '(missing)'):<{col_w}}" for l in table.labels
        )
        marker = "" if row.is_uniform() else " *"
        print(f"{row.key:<{key_w}}  {vals}{marker}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envsnap pivot",
        description="Pivot multiple snapshots into a comparison table.",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help="Snapshot JSON files")
    p.add_argument("--summary", action="store_true", help="Print summary line only")
    p.add_argument("--differing-only", action="store_true", help="Show only differing keys")
    p.add_argument("--json", action="store_true", help="Output as JSON")
    return p


def main(argv: List[str] | None = None) -> None:  # pragma: no cover
    ns = build_parser().parse_args(argv)
    cmd_pivot(ns)
