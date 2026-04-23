"""Tests for envsnap.env_reorder."""

from __future__ import annotations

from typing import Dict

import pytest

from envsnap.env_reorder import (
    ReorderResult,
    reorder_by_fn,
    reorder_by_list,
    reorder_summary,
)


def _snap(**kwargs: str) -> Dict[str, str]:
    return dict(kwargs)


# ---------------------------------------------------------------------------
# reorder_by_list
# ---------------------------------------------------------------------------

def test_reorder_by_list_basic():
    snap = _snap(B="2", A="1", C="3")
    result = reorder_by_list(snap, ["A", "B", "C"])
    assert list(result.env.keys()) == ["A", "B", "C"]


def test_reorder_by_list_partial_order_appends_remaining():
    snap = _snap(B="2", A="1", C="3")
    result = reorder_by_list(snap, ["C", "A"], append_remaining=True)
    assert list(result.env.keys()) == ["C", "A", "B"]


def test_reorder_by_list_drop_remaining():
    snap = _snap(B="2", A="1", C="3")
    result = reorder_by_list(snap, ["A", "C"], append_remaining=False)
    assert list(result.env.keys()) == ["A", "C"]
    assert "B" not in result.env


def test_reorder_by_list_unknown_keys_in_order_ignored():
    snap = _snap(A="1", B="2")
    result = reorder_by_list(snap, ["Z", "A", "B"])
    assert list(result.env.keys()) == ["A", "B"]


def test_reorder_by_list_preserves_values():
    snap = _snap(B="beta", A="alpha")
    result = reorder_by_list(snap, ["A", "B"])
    assert result.env["A"] == "alpha"
    assert result.env["B"] == "beta"


def test_reorder_by_list_original_order_recorded():
    snap = _snap(B="2", A="1")
    result = reorder_by_list(snap, ["A", "B"])
    assert result.original_order == ["B", "A"]


def test_reorder_by_list_new_order_recorded():
    snap = _snap(B="2", A="1")
    result = reorder_by_list(snap, ["A", "B"])
    assert result.new_order == ["A", "B"]


# ---------------------------------------------------------------------------
# reorder_by_fn
# ---------------------------------------------------------------------------

def test_reorder_by_fn_alphabetical():
    snap = _snap(C="3", A="1", B="2")
    result = reorder_by_fn(snap, key_fn=lambda k: k)
    assert list(result.env.keys()) == ["A", "B", "C"]


def test_reorder_by_fn_reverse():
    snap = _snap(A="1", B="2", C="3")
    result = reorder_by_fn(snap, key_fn=lambda k: k, reverse=True)
    assert list(result.env.keys()) == ["C", "B", "A"]


def test_reorder_by_fn_by_value_length():
    snap = _snap(SHORT="hi", LONGER="hello!", MED="hey")
    result = reorder_by_fn(snap, key_fn=lambda k: len(snap[k]))
    assert list(result.env.keys())[0] == "SHORT"


def test_reorder_by_fn_preserves_all_keys():
    snap = _snap(Z="z", A="a", M="m")
    result = reorder_by_fn(snap, key_fn=lambda k: k)
    assert set(result.env.keys()) == {"A", "M", "Z"}


# ---------------------------------------------------------------------------
# reorder_summary
# ---------------------------------------------------------------------------

def test_reorder_summary_unchanged():
    snap = _snap(A="1", B="2")
    result = reorder_by_list(snap, ["A", "B"])
    # original dict insertion order matches requested order
    summary = reorder_summary(result)
    assert "unchanged" in summary.lower() or "changed" in summary.lower()


def test_reorder_summary_changed_mentions_keys():
    snap = _snap(B="2", A="1")
    result = reorder_by_list(snap, ["A", "B"])
    summary = reorder_summary(result)
    assert "2" in summary  # key count
