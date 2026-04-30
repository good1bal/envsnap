"""Tests for envsnap.cli_version."""
from __future__ import annotations

import argparse
import json
import pytest

from envsnap.env_version import VersionStore, add_version, save_versions
from envsnap.cli_version import cmd_add, cmd_list, cmd_show


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {"store": "/tmp/test_versions.json", "label": "snap", "json": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _prepopulated_store(tmp_path):
    path = str(tmp_path / "v.json")
    store = VersionStore()
    add_version(store, label="first", env={"A": "1"})
    add_version(store, label="second", env={"A": "2", "B": "3"})
    save_versions(path, store)
    return path


def test_cmd_list_empty_store(tmp_path, capsys):
    ns = _ns(store=str(tmp_path / "v.json"))
    cmd_list(ns)
    out = capsys.readouterr().out
    assert "No versions" in out


def test_cmd_list_shows_versions(tmp_path, capsys):
    path = _prepopulated_store(tmp_path)
    ns = _ns(store=path)
    cmd_list(ns)
    out = capsys.readouterr().out
    assert "v1" in out
    assert "first" in out
    assert "v2" in out
    assert "second" in out


def test_cmd_list_json_output(tmp_path, capsys):
    path = _prepopulated_store(tmp_path)
    ns = _ns(store=path, json=True)
    cmd_list(ns)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert len(data) == 2
    assert data[0]["version"] == 1
    assert data[1]["label"] == "second"


def test_cmd_show_version(tmp_path, capsys):
    path = _prepopulated_store(tmp_path)
    ns = _ns(store=path, version=1)
    cmd_show(ns)
    out = capsys.readouterr().out
    assert "first" in out
    assert "A=1" in out


def test_cmd_show_json(tmp_path, capsys):
    path = _prepopulated_store(tmp_path)
    ns = _ns(store=path, version=2, json=True)
    cmd_show(ns)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["version"] == 2
    assert data["env"]["B"] == "3"


def test_cmd_show_missing_version_exits(tmp_path):
    path = _prepopulated_store(tmp_path)
    ns = _ns(store=path, version=99)
    with pytest.raises(SystemExit) as exc:
        cmd_show(ns)
    assert exc.value.code == 1


def test_cmd_add_records_version(tmp_path, monkeypatch, capsys):
    path = str(tmp_path / "v.json")
    monkeypatch.setenv("MY_KEY", "hello")
    ns = _ns(store=path, label="ci-deploy")
    cmd_add(ns)
    out = capsys.readouterr().out
    assert "v1" in out
    assert "ci-deploy" in out
