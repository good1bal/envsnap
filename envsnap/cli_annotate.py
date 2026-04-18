"""CLI commands for annotating snapshots stored in history."""
from __future__ import annotations

import argparse
import json
import sys

from envsnap.annotate import annotate, annotation_summary, filter_by_tag
from envsnap.history import load_history, save_history


def cmd_annotate(args: argparse.Namespace) -> None:
    """Add a note/tags to a snapshot in history by label."""
    history = load_history(args.history_file)
    if not history:
        print("History is empty.", file=sys.stderr)
        sys.exit(1)

    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
    updated = False
    new_history = []
    for snap in history:
        if snap.get("label") == args.label:
            snap = annotate(snap, note=args.note or "", tags=tags)
            updated = True
        new_history.append(snap)

    if not updated:
        print(f"Label '{args.label}' not found in history.", file=sys.stderr)
        sys.exit(1)

    save_history(args.history_file, new_history)
    print(f"Annotated snapshot '{args.label}'.")


def cmd_filter_tag(args: argparse.Namespace) -> None:
    """List snapshots in history that carry a given tag."""
    history = load_history(args.history_file)
    matches = filter_by_tag(history, args.tag)
    if not matches:
        print(f"No snapshots tagged '{args.tag}'.")
        return
    for snap in matches:
        label = snap.get("label", "?")
        summary = annotation_summary(snap)
        print(f"  {label}  {summary}")


def cmd_show_annotation(args: argparse.Namespace) -> None:
    """Print the annotation for a specific snapshot label."""
    history = load_history(args.history_file)
    for snap in history:
        if snap.get("label") == args.label:
            print(annotation_summary(snap))
            return
    print(f"Label '{args.label}' not found.", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(prog="envsnap-annotate")
    parser.add_argument("--history-file", default=".envsnap_history.json")
    sub = parser.add_subparsers(dest="cmd")

    p_ann = sub.add_parser("add", help="Annotate a snapshot")
    p_ann.add_argument("label")
    p_ann.add_argument("--note", default="")
    p_ann.add_argument("--tags", default="", help="Comma-separated tags")
    p_ann.set_defaults(func=cmd_annotate)

    p_ft = sub.add_parser("filter", help="Filter snapshots by tag")
    p_ft.add_argument("tag")
    p_ft.set_defaults(func=cmd_filter_tag)

    p_show = sub.add_parser("show", help="Show annotation for a label")
    p_show.add_argument("label")
    p_show.set_defaults(func=cmd_show_annotation)

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
