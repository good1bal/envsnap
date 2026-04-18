"""Tests for envsnap.tag_index."""
import pytest

from envsnap.annotate import annotate
from envsnap.tag_index import (
    all_tags,
    build_tag_index,
    merge_indexes,
    snapshots_for_tag,
)


def _snap(label: str, env: dict | None = None) -> dict:
    base = {"label": label, "env": env or {}, "captured_at": "2024-01-01T00:00:00", "checksum": "abc"}
    return base


def test_build_tag_index_empty_list():
    assert build_tag_index([]) == {}


def test_build_tag_index_no_annotations():
    snaps = [_snap("s1"), _snap("s2")]
    assert build_tag_index(snaps) == {}


def test_build_tag_index_single_tag():
    snap = annotate(_snap("prod"), tags=["production"])
    index = build_tag_index([snap])
    assert "production" in index
    assert index["production"] == ["prod"]


def test_build_tag_index_multiple_tags():
    snap = annotate(_snap("s1"), tags=["ci", "staging"])
    index = build_tag_index([snap])
    assert set(index.keys()) == {"ci", "staging"}


def test_build_tag_index_multiple_snapshots_same_tag():
    s1 = annotate(_snap("alpha"), tags=["release"])
    s2 = annotate(_snap("beta"), tags=["release"])
    index = build_tag_index([s1, s2])
    assert sorted(index["release"]) == ["alpha", "beta"]


def test_snapshots_for_tag_found():
    s1 = annotate(_snap("x"), tags=["foo"])
    index = build_tag_index([s1])
    assert snapshots_for_tag(index, "foo") == ["x"]


def test_snapshots_for_tag_missing():
    assert snapshots_for_tag({}, "nope") == []


def test_all_tags_sorted():
    s1 = annotate(_snap("s1"), tags=["z", "a", "m"])
    index = build_tag_index([s1])
    assert all_tags(index) == ["a", "m", "z"]


def test_merge_indexes_disjoint():
    idx1 = {"a": ["s1"]}
    idx2 = {"b": ["s2"]}
    merged = merge_indexes(idx1, idx2)
    assert merged == {"a": ["s1"], "b": ["s2"]}


def test_merge_indexes_overlapping_deduplicates():
    idx1 = {"a": ["s1", "s2"]}
    idx2 = {"a": ["s2", "s3"]}
    merged = merge_indexes(idx1, idx2)
    assert merged[1", "s2", "s3"]
