"""Tests for envsnap.env_template."""
import pytest
from envsnap.env_template import (
    build_template,
    apply_template,
    template_diff,
    template_summary,
    TemplateMissingKey,
)


def _snap(env: dict) -> dict:
    return {"label": "test", "env": env}


def test_build_template_keys_preserved():
    snap = _snap({"DB_HOST": "localhost", "PORT": "5432"})
    tmpl = build_template(snap)
    assert set(tmpl.keys()) == {"DB_HOST", "PORT"}


def test_build_template_values_empty():
    snap = _snap({"DB_HOST": "localhost", "PORT": "5432"})
    tmpl = build_template(snap)
    assert all(v == "" for v in tmpl.values())


def test_build_template_empty_env():
    snap = _snap({})
    assert build_template(snap) == {}


def test_apply_template_fills_values():
    tmpl = {"DB_HOST": "", "PORT": ""}
    filled = apply_template(tmpl, {"DB_HOST": "prod-db", "PORT": "5432"})
    assert filled == {"DB_HOST": "prod-db", "PORT": "5432"}


def test_apply_template_missing_key_raises():
    tmpl = {"DB_HOST": "", "PORT": ""}
    with pytest.raises(TemplateMissingKey):
        apply_template(tmpl, {"DB_HOST": "prod-db"})


def test_apply_template_allow_missing():
    tmpl = {"DB_HOST": "", "PORT": ""}
    filled = apply_template(tmpl, {"DB_HOST": "prod-db"}, allow_missing=True)
    assert filled["PORT"] == ""
    assert filled["DB_HOST"] == "prod-db"


def test_template_diff_missing_in_snapshot():
    tmpl = {"DB_HOST": "", "PORT": "", "SECRET": ""}
    snap = _snap({"DB_HOST": "localhost"})
    diff = template_diff(tmpl, snap)
    assert "PORT" in diff["missing_in_snapshot"]
    assert "SECRET" in diff["missing_in_snapshot"]


def test_template_diff_extra_in_snapshot():
    tmpl = {"DB_HOST": ""}
    snap = _snap({"DB_HOST": "localhost", "EXTRA": "val"})
    diff = template_diff(tmpl, snap)
    assert diff["extra_in_snapshot"] == ["EXTRA"]


def test_template_diff_exact_match():
    tmpl = {"DB_HOST": ""}
    snap = _snap({"DB_HOST": "localhost"})
    diff = template_diff(tmpl, snap)
    assert diff["missing_in_snapshot"] == []
    assert diff["extra_in_snapshot"] == []


def test_template_summary_no_diff():
    diff = {"missing_in_snapshot": [], "extra_in_snapshot": []}
    assert template_summary(diff) == "Template matches snapshot."


def test_template_summary_with_missing():
    diff = {"missing_in_snapshot": ["PORT"], "extra_in_snapshot": []}
    out = template_summary(diff)
    assert "PORT" in out
    assert "Missing" in out


def test_template_summary_with_extra():
    diff = {"missing_in_snapshot": [], "extra_in_snapshot": ["EXTRA"]}
    out = template_summary(diff)
    assert "EXTRA" in out
    assert "Extra" in out
