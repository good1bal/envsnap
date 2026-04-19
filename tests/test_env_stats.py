"""Tests for envsnap.env_stats."""
import pytest
from envsnap.env_stats import compute_stats, stats_summary, EnvStats


def _env(**kwargs: str):
    return dict(kwargs)


def test_compute_stats_empty_env():
    stats = compute_stats({})
    assert stats.total_keys == 0
    assert stats.unique_values == 0
    assert stats.empty_values == 0


def test_compute_stats_total_keys():
    env = _env(A="1", B="2", C="3")
    stats = compute_stats(env)
    assert stats.total_keys == 3


def test_compute_stats_empty_values():
    env = _env(A="", B="", C="hello")
    stats = compute_stats(env)
    assert stats.empty_values == 2


def test_compute_stats_unique_values():
    env = _env(A="x", B="y", C="x")
    stats = compute_stats(env)
    assert stats.unique_values == 2


def test_compute_stats_duplicate_values():
    env = _env(A="x", B="x", C="z")
    stats = compute_stats(env)
    assert stats.duplicate_values == 1


def test_compute_stats_no_duplicates():
    env = _env(A="1", B="2", C="3")
    stats = compute_stats(env)
    assert stats.duplicate_values == 0


def test_compute_stats_avg_key_length():
    env = {"AB": "v", "ABCD": "v"}  # lengths 2 and 4 -> avg 3.0
    stats = compute_stats(env)
    assert stats.avg_key_length == 3.0


def test_compute_stats_longest_shortest_key():
    env = {"A": "1", "LONGKEY": "2", "MED": "3"}
    stats = compute_stats(env)
    assert stats.longest_key == "LONGKEY"
    assert stats.shortest_key == "A"


def test_compute_stats_prefix_counts():
    env = {"APP_HOST": "localhost", "APP_PORT": "8080", "DB_HOST": "db"}
    stats = compute_stats(env)
    assert stats.prefix_counts.get("APP") == 2
    assert stats.prefix_counts.get("DB") == 1


def test_compute_stats_no_prefixes():
    env = {"HOST": "localhost", "PORT": "8080"}
    stats = compute_stats(env)
    assert stats.prefix_counts == {}


def test_stats_summary_contains_total(capsys):
    env = _env(A="1", B="2")
    stats = compute_stats(env)
    summary = stats_summary(stats)
    assert "Total keys" in summary
    assert "2" in summary


def test_stats_summary_shows_prefix_section():
    env = {"APP_X": "1", "APP_Y": "2"}
    stats = compute_stats(env)
    summary = stats_summary(stats)
    assert "APP" in summary
    assert "Prefix counts" in summary


def test_stats_summary_no_prefix_section_when_empty():
    env = {"HOST": "h", "PORT": "p"}
    stats = compute_stats(env)
    summary = stats_summary(stats)
    assert "Prefix counts" not in summary
