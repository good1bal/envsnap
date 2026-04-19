"""CLI commands for patching snapshots."""
from __future__ import annotations
import argparse
import json
import os
from envsnap.env_patch import PatchOperation, apply_patch, patch_summary
from envsnap.snapshot import load, save


def _load_ops_from_args(ns: argparse.Namespace) -> list[PatchOperation]:
    ops: list[PatchOperation] = []
    for item in ns.set or []:
        key, _, value = item.partition("=")
        ops.append(PatchOperation(op="set", key=key, value=value))
    for key in ns.delete or []:
        ops.append(PatchOperation(op="delete", key=key))
    for item in ns.rename or []:
        old, _, new = item.partition(":")
        ops.append(PatchOperation(op="rename", key=old, new_key=new))
    return ops


def cmd_patch(ns: argparse.Namespace) -> None:
    snap = load(ns.file)
    ops = _load_ops_from_args(ns)
    result = apply_patch(snap["env"], ops, strict=ns.strict)
    if ns.dry_run:
        print(patch_summary(result))
        return
    snap["env"] = result.patched
    out = ns.output or ns.file
    save(snap, out)
    print(patch_summary(result))
    print(f"Saved to {out}")


def cmd_patch_json(ns: argparse.Namespace) -> None:
    """Apply ops from a JSON file: [{"op":"set","key":"K","value":"V"}, ...]"""
    with open(ns.ops_file) as f:
        raw = json.load(f)
    ops = [
        PatchOperation(
            op=o["op"],
            key=o["key"],
            value=o.get("value"),
            new_key=o.get("new_key"),
        )
        for o in raw
    ]
    snap = load(ns.file)
    result = apply_patch(snap["env"], ops, strict=ns.strict)
    snap["env"] = result.patched
    out = ns.output or ns.file
    save(snap, out)
    print(patch_summary(result))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="envsnap patch", description="Patch a snapshot")
    p.add_argument("file", help="Snapshot file")
    p.add_argument("--set", metavar="KEY=VALUE", action="append")
    p.add_argument("--delete", metavar="KEY", action="append")
    p.add_argument("--rename", metavar="OLD:NEW", action="append")
    p.add_argument("--output", "-o", metavar="FILE")
    p.add_argument("--strict", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    return p


def main() -> None:
    parser = build_parser()
    ns = parser.parse_args()
    cmd_patch(ns)


if __name__ == "__main__":
    main()
