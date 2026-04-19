"""Tests for envsnap.env_promote."""
import pytest
from envsnap.env_promote import promote, promote_summary, PromoteResult


def _snap(env: dict, label: str = "test") -> dict:
    return {"label": label, "env": env}


SRC = _snap({"DB_HOST": "prod-db", "DB_PORT": "5432", "SECRET": "s3cr3t"}, label="prod")
TGT = _snap({"DB_HOST": "staging-db", "APP_ENV": "staging"}, label="staging")


def test_promote_adds_new_keys():
    result = promote(SRC, TGT, "prod", "staging", keys=["DB_PORT"])
    assert result.promoted["DB_PORT"] == "5432"


def test_promote_skips_existing_key_without_overwrite():
    result = promote(SRC, TGT, "prod", "staging", keys=["DB_HOST"])
    assert "DB_HOST" in result.skipped
    assert result.promoted["DB_HOST"] == "staging-db"


def test_promote_overwrites_existing_key_with_flag():
    result = promote(SRC, TGT, "prod", "staging", keys=["DB_HOST"], overwrite=True)
    assert result.promoted["DB_HOST"] == "prod-db"
    assert "DB_HOST" in result.overwritten


def test_promote_skips_missing_source_key():
    result = promote(SRC, TGT, "prod", "staging", keys=["NONEXISTENT"])
    assert "NONEXISTENT" in result.skipped


def test_promote_all_keys_when_none_specified():
    src = _snap({"A": "1", "B": "2"}, label="prod")
    tgt = _snap({}, label="staging")
    result = promote(src, tgt, "prod", "staging")
    assert result.promoted["A"] == "1"
    assert result.promoted["B"] == "2"


def test_promote_preserves_existing_target_keys():
    result = promote(SRC, TGT, "prod", "staging", keys=["DB_PORT"])
    assert result.promoted["APP_ENV"] == "staging"


def test_promote_result_labels():
    result = promote(SRC, TGT, "prod", "staging")
    assert result.source_label == "prod"
    assert result.target_label == "staging"


def test_promote_summary_contains_labels():
    result = promote(SRC, TGT, "prod", "staging", keys=["DB_PORT"])
    summary = promote_summary(result)
    assert "prod" in summary
    assert "staging" in summary


def test_promote_summary_lists_skipped():
    result = promote(SRC, TGT, "prod", "staging", keys=["DB_HOST", "DB_PORT"])
    summary = promote_summary(result)
    assert "DB_HOST" in summary


def test_promote_summary_lists_overwritten():
    result = promote(SRC, TGT, "prod", "staging", keys=["DB_HOST"], overwrite=True)
    summary = promote_summary(result)
    assert "DB_HOST" in summary
    assert "Overwritten" in summary


def test_promote_empty_keys_list():
    result = promote(SRC, TGT, "prod", "staging", keys=[])
    assert result.promoted == dict(TGT["env"])
    assert result.skipped == []
