"""Tests for envsnap.env_diff_score."""
import pytest

from envsnap.env_diff_score import DiffScore, score, score_summary


def _snap(label: str, env: dict) -> dict:
    return {"label": label, "env": env, "checksum": "x"}


# ---------------------------------------------------------------------------
# score()
# ---------------------------------------------------------------------------

def test_score_returns_diff_score():
    a = _snap("a", {"K": "1"})
    b = _snap("b", {"K": "1"})
    result = score(a, b)
    assert isinstance(result, DiffScore)


def test_score_identical_snapshots_similarity_one():
    env = {"A": "1", "B": "2"}
    a = _snap("a", env)
    b = _snap("b", env)
    ds = score(a, b)
    assert ds.similarity == 1.0
    assert ds.divergence == 0.0


def test_score_completely_disjoint_snapshots():
    a = _snap("a", {"X": "1"})
    b = _snap("b", {"Y": "2"})
    ds = score(a, b)
    # X removed, Y added — 2 changed out of 2 total keys
    assert ds.divergence == 1.0
    assert ds.similarity == 0.0


def test_score_partial_overlap():
    a = _snap("a", {"A": "1", "B": "2", "C": "3"})
    b = _snap("b", {"A": "1", "B": "99", "D": "4"})
    ds = score(a, b)
    # unchanged: A(1), changed: B, removed: C, added: D  → total=4, diff=3
    assert ds.unchanged == 1
    assert ds.changed == 1
    assert ds.removed == 1
    assert ds.added == 1
    assert ds.total_keys == 4
    assert ds.divergence == pytest.approx(0.75)
    assert ds.similarity == pytest.approx(0.25)


def test_score_empty_snapshots():
    a = _snap("a", {})
    b = _snap("b", {})
    ds = score(a, b)
    assert ds.total_keys == 0
    assert ds.similarity == 1.0
    assert ds.divergence == 0.0


def test_score_labels_from_snapshot():
    a = _snap("prod", {"K": "v"})
    b = _snap("staging", {"K": "v"})
    ds = score(a, b)
    assert ds.label_a == "prod"
    assert ds.label_b == "staging"


def test_score_breakdown_keys_present():
    a = _snap("a", {"K": "1"})
    b = _snap("b", {"K": "2"})
    ds = score(a, b)
    assert "added_ratio" in ds.breakdown
    assert "removed_ratio" in ds.breakdown
    assert "changed_ratio" in ds.breakdown
    assert "unchanged_ratio" in ds.breakdown


def test_score_breakdown_ratios_sum_to_one():
    a = _snap("a", {"A": "1", "B": "2"})
    b = _snap("b", {"A": "9", "C": "3"})
    ds = score(a, b)
    total = sum(ds.breakdown.values())
    assert total == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# score_summary()
# ---------------------------------------------------------------------------

def test_score_summary_contains_labels():
    a = _snap("alpha", {"K": "v"})
    b = _snap("beta", {"K": "v"})
    ds = score(a, b)
    s = score_summary(ds)
    assert "alpha" in s
    assert "beta" in s


def test_score_summary_contains_similarity():
    a = _snap("a", {"K": "v"})
    b = _snap("b", {"K": "v"})
    ds = score(a, b)
    s = score_summary(ds)
    assert "100.0%" in s or "similarity" in s


def test_score_summary_shows_counts():
    a = _snap("a", {"X": "1"})
    b = _snap("b", {"Y": "2"})
    ds = score(a, b)
    s = score_summary(ds)
    assert "+1" in s
    assert "-1" in s
