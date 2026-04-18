import json
import pytest
from envsnap.env_alias import (
    load_aliases,
    save_aliases,
    add_alias,
    remove_alias,
    resolve,
    apply_aliases,
    reverse_map,
)


@pytest.fixture
def store(tmp_path):
    return str(tmp_path)


def test_load_aliases_missing_file_returns_empty(store):
    assert load_aliases(store) == {}


def test_add_alias_creates_entry(store):
    result = add_alias("db_url", "DATABASE_URL", store)
    assert result["db_url"] == "DATABASE_URL"


def test_add_alias_persists(store):
    add_alias("db_url", "DATABASE_URL", store)
    loaded = load_aliases(store)
    assert loaded["db_url"] == "DATABASE_URL"


def test_add_multiple_aliases(store):
    add_alias("db_url", "DATABASE_URL", store)
    add_alias("secret", "SECRET_KEY", store)
    loaded = load_aliases(store)
    assert len(loaded) == 2


def test_remove_alias(store):
    add_alias("db_url", "DATABASE_URL", store)
    remove_alias("db_url", store)
    assert load_aliases(store) == {}


def test_remove_nonexistent_alias_is_safe(store):
    result = remove_alias("ghost", store)
    assert result == {}


def test_resolve_known_alias():
    aliases = {"db_url": "DATABASE_URL"}
    assert resolve("db_url", aliases) == "DATABASE_URL"


def test_resolve_unknown_returns_key():
    assert resolve("UNKNOWN", {}) == "UNKNOWN"


def test_apply_aliases_adds_alias_key():
    env = {"DATABASE_URL": "postgres://localhost/db"}
    aliases = {"db_url": "DATABASE_URL"}
    result = apply_aliases(env, aliases)
    assert result["db_url"] == "postgres://localhost/db"
    assert result["DATABASE_URL"] == "postgres://localhost/db"


def test_apply_aliases_skips_missing_real_key():
    env = {"OTHER": "value"}
    aliases = {"db_url": "DATABASE_URL"}
    result = apply_aliases(env, aliases)
    assert "db_url" not in result


def test_reverse_map_single():
    aliases = {"db_url": "DATABASE_URL"}
    rev = reverse_map(aliases)
    assert rev == {"DATABASE_URL": ["db_url"]}


def test_reverse_map_multiple_aliases_same_key():
    aliases = {"db_url": "DATABASE_URL", "database": "DATABASE_URL"}
    rev = reverse_map(aliases)
    assert set(rev["DATABASE_URL"]) == {"db_url", "database"}
