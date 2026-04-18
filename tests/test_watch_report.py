"""Tests for envsnap.watch_report."""
from __future__ import annotations

import pytest

from envsnap.diff import DiffResult
from envsnap.watch import WatchSession, WatchEvent
from envsnap.watch_report import format_watch_report, watch_summary


def _session(events=None, polls=5, label="test", interval=1.0):
    s = WatchSession(label=label, interval=interval, polls=polls)
    if events:
        s.events.extend(events)
    return s


def _event(added=None, removed=None, changed=None, poll_index=0):
    diff = DiffResult(
        added=set(added or []),
        removed=set(removed or []),
        changed={k: ("old", "new") for k in (changed or [])},
        unchanged={},
    )
    return WatchEvent(timestamp=1000.0, diff=diff, poll_index=poll_index)


def test_format_no_changes():
    session = _session()
    report = format_watch_report(session)
    assert "No changes detected" in report
    assert "test" in report


def test_format_shows_added_key():
    event = _event(added=["NEW_VAR"])
    session = _session(events=[event])
    report = format_watch_report(session)
    assert "NEW_VAR" in report
    assert "+" in report


def test_format_shows_removed_key():
    event = _event(removed=["OLD_VAR"])
    session = _session(events=[event])
    report = format_watch_report(session)
    assert "OLD_VAR" in report
    assert "-" in report


def test_format_shows_changed_key():
    event = _event(changed=["SOME_KEY"])
    session = _session(events=[event])
    report = format_watch_report(session)
    assert "SOME_KEY" in report
    assert "~" in report


def test_summary_no_changes():
    session = _session(polls=4)
    s = watch_summary(session)
    assert "No changes" in s
    assert "4" in s


def test_summary_with_changes():
    event = _event(added=["X"], removed=["Y"])
    session = _session(events=[event], polls=3)
    s = watch_summary(session)
    assert "1 change event" in s
    assert "2 total key changes" in s
