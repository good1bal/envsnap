"""Tests for envsnap.watch."""
from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from envsnap.watch import watch, WatchSession, WatchEvent
from envsnap.snapshot import capture


def _make_env(extra=None):
    base = {"HOME": "/home/user", "PATH": "/usr/bin"}
    if extra:
        base.update(extra)
    return base


def test_watch_returns_session_no_changes():
    env = _make_env()
    with patch("envsnap.watch.time.sleep"), \
         patch("envsnap.watch.capture", return_value={"vars": env, "label": "w", "checksum": "x"}):
        session = watch(label="w", interval=0, max_polls=3)
    assert isinstance(session, WatchSession)
    assert session.polls == 3
    assert not session.has_changes()


def test_watch_detects_added_key():
    base_snap = {"vars": {"A": "1"}, "label": "w", "checksum": "a"}
    changed_snap = {"vars": {"A": "1", "B": "2"}, "label": "w", "checksum": "b"}
    side_effects = [base_snap, changed_snap, changed_snap]

    with patch("envsnap.watch.time.sleep"), \
         patch("envsnap.watch.capture", side_effect=[base_snap] + side_effects):
        session = watch(label="w", interval=0, max_polls=3)

    assert session.has_changes()
    assert any("B" in e.diff.added for e in session.events)


def test_watch_detects_removed_key():
    base_snap = {"vars": {"A": "1", "B": "2"}, "label": "w", "checksum": "a"}
    changed_snap = {"vars": {"A": "1"}, "label": "w", "checksum": "b"}

    with patch("envsnap.watch.time.sleep"), \
         patch("envsnap.watch.capture", side_effect=[base_snap, changed_snap, changed_snap, changed_snap]):
        session = watch(label="w", interval=0, max_polls=3)

    assert any("B" in e.diff.removed for e in session.events)


def test_watch_total_changes():
    base_snap = {"vars": {"A": "1"}, "label": "w", "checksum": "a"}
    snap2 = {"vars": {"A": "1", "B": "2"}, "label": "w", "checksum": "b"}
    snap3 = {"vars": {"A": "1", "B": "2", "C": "3"}, "label": "w", "checksum": "c"}

    with patch("envsnap.watch.time.sleep"), \
         patch("envsnap.watch.capture", side_effect=[base_snap, snap2, snap3]):
        session = watch(label="w", interval=0, max_polls=2)

    assert session.total_changes() >= 2


def test_on_change_callback_called():
    base_snap = {"vars": {"A": "1"}, "label": "w", "checksum": "a"}
    changed_snap = {"vars": {"A": "2"}, "label": "w", "checksum": "b"}
    calls = []

    with patch("envsnap.watch.time.sleep"), \
         patch("envsnap.watch.capture", side_effect=[base_snap, changed_snap]):
        watch(label="w", interval=0, max_polls=1, on_change=calls.append)

    assert len(calls) == 1
    assert isinstance(calls[0], WatchEvent)
