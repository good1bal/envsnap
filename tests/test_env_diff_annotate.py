"""Tests for envsnap.env_diff_annotate."""
import pytest

from envsnap.diff import DiffResult
from envsnap.env_diff_annotate import (
    AnnotatedDiff,
    AnnotatedEntry,
    annotate_diff,
    annotated_diff_summary,
)


def _make_result(
    added=None, removed=None, changed=None, unchanged=None,
    label_a="snap-a", label_b="snap-b",
):
    snap_a = {"label": label_a, "env": {}}
    snap_b = {"label": label_b, "env": {}}

    for k in (removed or []):
        snap_a["env"][k] = f"old_{k}"
    for k in (unchanged or []):
        snap_a["env"][k] = f"val_{k}"
        snap_b["env"][k] = f"val_{k}"
    for k, (old, new) in (changed or {}).items():
        snap_a["env"][k] = old
        snap_b["env"][k] = new
    for k in (added or []):
        snap_b["env"][k] = f"new_{k}"

    return DiffResult(
        snapshot_a=snap_a,
        snapshot_b=snap_b,
        added=list(added or []),
        removed=list(removed or []),
        changed=dict(changed or {}),
        unchanged=list(unchanged or []),
    )


def test_annotate_diff_returns_annotated_diff():
    result = _make_result(added=["NEW_KEY"])
    ad = annotate_diff(result)
    assert isinstance(ad, AnnotatedDiff)


def test_annotate_diff_labels_preserved():
    result = _make_result(label_a="prod", label_b="staging")
    ad = annotate_diff(result)
    assert ad.label_a == "prod"
    assert ad.label_b == "staging"


def test_annotate_diff_added_entry():
    result = _make_result(added=["FOO"])
    ad = annotate_diff(result)
    added = ad.by_status("added")
    assert len(added) == 1
    assert added[0].key == "FOO"
    assert added[0].old_value is None


def test_annotate_diff_removed_entry():
    result = _make_result(removed=["BAR"])
    ad = annotate_diff(result)
    removed = ad.by_status("removed")
    assert len(removed) == 1
    assert removed[0].key == "BAR"
    assert removed[0].new_value is None


def test_annotate_diff_changed_entry():
    result = _make_result(changed={"HOST": ("localhost", "prod.host")})
    ad = annotate_diff(result)
    changed = ad.by_status("changed")
    assert len(changed) == 1
    assert changed[0].old_value == "localhost"
    assert changed[0].new_value == "prod.host"


def test_annotate_diff_unchanged_entry():
    result = _make_result(unchanged=["PORT"])
    ad = annotate_diff(result)
    unchanged = ad.by_status("unchanged")
    assert len(unchanged) == 1
    assert unchanged[0].key == "PORT"


def test_annotate_diff_notes_attached():
    result = _make_result(added=["NEW_KEY"])
    ad = annotate_diff(result, notes={"NEW_KEY": "added in v2"})
    entry = ad.by_status("added")[0]
    assert entry.note == "added in v2"


def test_annotate_diff_tags_attached():
    result = _make_result(changed={"SECRET": ("old", "new")})
    ad = annotate_diff(result, tags={"SECRET": ["sensitive", "security"]})
    entry = ad.by_status("changed")[0]
    assert "sensitive" in entry.tags
    assert "security" in entry.tags


def test_annotate_diff_tagged_filter():
    result = _make_result(added=["A"], removed=["B"])
    ad = annotate_diff(result, tags={"A": ["infra"]})
    infra = ad.tagged("infra")
    assert len(infra) == 1
    assert infra[0].key == "A"


def test_annotate_diff_entries_sorted_by_key():
    result = _make_result(added=["ZEBRA", "ALPHA", "MANGO"])
    ad = annotate_diff(result)
    keys = [e.key for e in ad.entries]
    assert keys == sorted(keys)


def test_annotate_diff_len():
    result = _make_result(added=["X"], removed=["Y"], unchanged=["Z"])
    ad = annotate_diff(result)
    assert len(ad) == 3


def test_annotated_diff_summary_format():
    result = _make_result(
        added=["A"], removed=["B"],
        changed={"C": ("old", "new")}, unchanged=["D"],
        label_a="v1", label_b="v2",
    )
    ad = annotate_diff(result)
    summary = annotated_diff_summary(ad)
    assert "v1 -> v2" in summary
    assert "+1" in summary
    assert "-1" in summary
    assert "~1" in summary
    assert "=1" in summary


def test_annotated_diff_summary_noted_count():
    result = _make_result(added=["X", "Y"])
    ad = annotate_diff(result, notes={"X": "important"})
    summary = annotated_diff_summary(ad)
    assert "noted=1" in summary


def test_annotated_diff_summary_tagged_count():
    result = _make_result(added=["X", "Y"])
    ad = annotate_diff(result, tags={"X": ["t1"], "Y": ["t2"]})
    summary = annotated_diff_summary(ad)
    assert "tagged=2" in summary
