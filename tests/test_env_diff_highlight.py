"""Tests for envsnap.env_diff_highlight."""
import pytest
from envsnap.env_diff_highlight import (
    HighlightSpan,
    HighlightResult,
    highlight_diff,
    highlight_summary,
    highlight_many,
)


def test_highlight_diff_returns_highlight_result():
    result = highlight_diff("KEY", "hello", "hello")
    assert isinstance(result, HighlightResult)
    assert result.key == "KEY"


def test_highlight_diff_identical_values_no_changed_spans():
    result = highlight_diff("KEY", "same", "same")
    assert all(not s.changed for s in result.old_spans)
    assert all(not s.changed for s in result.new_spans)


def test_highlight_diff_fully_different_values():
    result = highlight_diff("KEY", "abc", "xyz")
    assert any(s.changed for s in result.old_spans)
    assert any(s.changed for s in result.new_spans)


def test_highlight_diff_partial_change():
    result = highlight_diff("KEY", "foobar", "foobaz")
    old_text = "".join(s.text for s in result.old_spans)
    new_text = "".join(s.text for s in result.new_spans)
    assert old_text == "foobar"
    assert new_text == "foobaz"


def test_highlight_diff_insertion():
    result = highlight_diff("KEY", "foo", "foobar")
    new_text = "".join(s.text for s in result.new_spans)
    assert new_text == "foobar"
    assert any(s.changed for s in result.new_spans)


def test_highlight_diff_deletion():
    result = highlight_diff("KEY", "foobar", "foo")
    old_text = "".join(s.text for s in result.old_spans)
    assert old_text == "foobar"
    assert any(s.changed for s in result.old_spans)


def test_highlight_diff_empty_old():
    result = highlight_diff("KEY", "", "new")
    assert len(result.old_spans) == 0
    new_text = "".join(s.text for s in result.new_spans)
    assert new_text == "new"


def test_highlight_diff_empty_new():
    result = highlight_diff("KEY", "old", "")
    old_text = "".join(s.text for s in result.old_spans)
    assert old_text == "old"
    assert len(result.new_spans) == 0


def test_highlight_summary_identical():
    result = highlight_diff("PORT", "8080", "8080")
    summary = highlight_summary(result)
    assert "PORT" in summary
    assert "->" in summary
    assert "[" not in summary  # no changed spans


def test_highlight_summary_changed_spans_use_brackets():
    result = highlight_diff("HOST", "localhost", "remotehost")
    summary = highlight_summary(result)
    assert "[" in summary
    assert "HOST" in summary


def test_highlight_summary_format():
    result = highlight_diff("X", "a", "b")
    summary = highlight_summary(result)
    assert "->" in summary
    assert summary.startswith("X:")


def test_highlight_many_returns_list():
    changed = {
        "A": ("old_a", "new_a"),
        "B": ("old_b", "new_b"),
    }
    results = highlight_many(changed)
    assert len(results) == 2
    assert {r.key for r in results} == {"A", "B"}


def test_highlight_many_empty():
    results = highlight_many({})
    assert results == []


def test_highlight_span_repr():
    span = HighlightSpan("abc", changed=True)
    assert isinstance(repr(span), str)


def test_highlight_result_repr():
    result = highlight_diff("K", "v1", "v2")
    r = repr(result)
    assert "K" in r
