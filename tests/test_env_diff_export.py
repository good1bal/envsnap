"""Tests for envsnap.env_diff_export."""
import csv
import io
import json

import pytest

from envsnap.diff import DiffResult
from envsnap.env_diff_export import to_csv, to_json, to_markdown


def _result(
    added=None,
    removed=None,
    changed=None,
    unchanged=None,
    label_a="snap-a",
    label_b="snap-b",
) -> DiffResult:
    return DiffResult(
        added=added or {},
        removed=removed or {},
        changed=changed or {},
        unchanged=unchanged or {},
        label_a=label_a,
        label_b=label_b,
    )


# --- to_json ---

def test_to_json_returns_valid_json():
    r = _result(added={"NEW": "1"})
    assert json.loads(to_json(r))  # no exception


def test_to_json_labels_present():
    r = _result(label_a="dev", label_b="prod")
    data = json.loads(to_json(r))
    assert data["label_a"] == "dev"
    assert data["label_b"] == "prod"


def test_to_json_added_keys():
    r = _result(added={"FOO": "bar"})
    data = json.loads(to_json(r))
    assert data["added"] == {"FOO": "bar"}


def test_to_json_changed_keys():
    r = _result(changed={"X": ("old", "new")})
    data = json.loads(to_json(r))
    assert data["changed"] == [{"key": "X", "before": "old", "after": "new"}]


def test_to_json_unchanged_keys():
    r = _result(unchanged={"A": "1", "B": "2"})
    data = json.loads(to_json(r))
    assert set(data["unchanged"]) == {"A", "B"}


def test_to_json_custom_indent():
    r = _result(added={"K": "v"})
    output = to_json(r, indent=4)
    assert "    " in output


# --- to_csv ---

def _parse_csv(text: str):
    reader = csv.DictReader(io.StringIO(text))
    return list(reader)


def test_to_csv_has_header():
    r = _result()
    rows = _parse_csv(to_csv(r))
    # no rows, but parsing must not fail
    assert isinstance(rows, list)


def test_to_csv_added_row():
    r = _result(added={"NEW": "yes"})
    rows = _parse_csv(to_csv(r))
    assert any(row["status"] == "added" and row["key"] == "NEW" for row in rows)


def test_to_csv_removed_row():
    r = _result(removed={"OLD": "gone"})
    rows = _parse_csv(to_csv(r))
    assert any(row["status"] == "removed" and row["key"] == "OLD" for row in rows)


def test_to_csv_changed_row_before_after():
    r = _result(changed={"VAR": ("v1", "v2")})
    rows = _parse_csv(to_csv(r))
    row = next(r for r in rows if r["key"] == "VAR")
    assert row["before"] == "v1"
    assert row["after"] == "v2"


def test_to_csv_unchanged_row_same_before_after():
    r = _result(unchanged={"STABLE": "x"})
    rows = _parse_csv(to_csv(r))
    row = next(r for r in rows if r["key"] == "STABLE")
    assert row["before"] == row["after"] == "x"


# --- to_markdown ---

def test_to_markdown_contains_header_row():
    r = _result()
    md = to_markdown(r)
    assert "| Status |" in md


def test_to_markdown_contains_labels():
    r = _result(label_a="dev", label_b="prod")
    md = to_markdown(r)
    assert "dev" in md and "prod" in md


def test_to_markdown_added_entry():
    r = _result(added={"NEW_KEY": "hello"})
    md = to_markdown(r)
    assert "added" in md
    assert "NEW_KEY" in md


def test_to_markdown_changed_entry_shows_before_and_after():
    r = _result(changed={"PORT": ("8080", "9090")})
    md = to_markdown(r)
    assert "8080" in md
    assert "9090" in md


def test_to_markdown_ends_with_newline():
    r = _result()
    assert to_markdown(r).endswith("\n")
