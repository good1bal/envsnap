"""Tests for envsnap.annotate."""
import pytest
from envsnap.annotate import (
    Annotation,
    annotate,
    get_annotation,
    filter_by_tag,
    annotation_summary,
)


def _snap(label: str = "test") -> dict:
    return {"label": label, "vars": {"HOME": "/home/user"}, "checksum": "abc"}


def test_annotate_adds_annotation_block():
    snap = annotate(_snap(), note="pre-deploy", tags=["prod"])
    assert "annotation" in snap


def test_annotate_preserves_existing_keys():
    snap = annotate(_snap(), note="x")
    assert snap["vars"] == {"HOME": "/home/user"}


def test_annotate_label_matches_snapshot():
    snap = annotate(_snap(label="deploy-42"), note="")
    ann = get_annotation(snap)
    assert ann.label == "deploy-42"


def test_annotate_tags_stored():
    snap = annotate(_snap(), tags=["staging", "v2"])
    ann = get_annotation(snap)
    assert ann.tags == ["staging", "v2"]


def test_get_annotation_returns_none_when_absent():
    assert get_annotation(_snap()) is None


def test_get_annotation_roundtrip():
    snap = annotate(_snap(), note="hello", tags=["a"])
    ann = get_annotation(snap)
    assert isinstance(ann, Annotation)
    assert ann.note == "hello"


def test_filter_by_tag_returns_matching():
    snaps = [
        annotate(_snap("s1"), tags=["prod"]),
        annotate(_snap("s2"), tags=["staging"]),
        annotate(_snap("s3"), tags=["prod", "hotfix"]),
    ]
    result = filter_by_tag(snaps, "prod")
    assert len(result) == 2


def test_filter_by_tag_excludes_unannotated():
    snaps = [_snap("bare"), annotate(_snap("tagged"), tags=["prod"])]
    result = filter_by_tag(snaps, "prod")
    assert len(result) == 1


def test_annotation_summary_no_annotation():
    assert annotation_summary(_snap()) == "(no annotation)"


def test_annotation_summary_with_data():
    snap = annotate(_snap(), note="ready", tags=["prod"])
    summary = annotation_summary(snap)
    assert "ready" in summary
    assert "prod" in summary
