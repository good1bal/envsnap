import pytest
from envsnap.env_diff_chain import build_chain, chain_summary, DiffChain, ChainLink


def _snap(label, env):
    return {"label": label, "env": env}


def test_build_chain_empty_list():
    chain = build_chain([])
    assert isinstance(chain, DiffChain)
    assert len(chain) == 0


def test_build_chain_single_snapshot():
    chain = build_chain([_snap("a", {"X": "1"})])
    assert len(chain) == 0


def test_build_chain_two_snapshots_creates_one_link():
    snaps = [
        _snap("v1", {"A": "1"}),
        _snap("v2", {"A": "1", "B": "2"}),
    ]
    chain = build_chain(snaps)
    assert len(chain) == 1
    assert chain.links[0].label_from == "v1"
    assert chain.links[0].label_to == "v2"


def test_build_chain_detects_added_key():
    snaps = [
        _snap("v1", {"A": "1"}),
        _snap("v2", {"A": "1", "B": "2"}),
    ]
    chain = build_chain(snaps)
    assert "B" in chain.links[0].result.added


def test_build_chain_detects_removed_key():
    snaps = [
        _snap("v1", {"A": "1", "B": "2"}),
        _snap("v2", {"A": "1"}),
    ]
    chain = build_chain(snaps)
    assert "B" in chain.links[0].result.removed


def test_build_chain_detects_changed_key():
    snaps = [
        _snap("v1", {"A": "old"}),
        _snap("v2", {"A": "new"}),
    ]
    chain = build_chain(snaps)
    assert "A" in chain.links[0].result.changed


def test_build_chain_three_snapshots():
    snaps = [
        _snap("v1", {"A": "1"}),
        _snap("v2", {"A": "1", "B": "2"}),
        _snap("v3", {"A": "1", "B": "2", "C": "3"}),
    ]
    chain = build_chain(snaps)
    assert len(chain) == 2
    assert chain.links[1].label_from == "v2"
    assert chain.links[1].label_to == "v3"


def test_total_added():
    snaps = [
        _snap("v1", {}),
        _snap("v2", {"A": "1"}),
        _snap("v3", {"A": "1", "B": "2"}),
    ]
    chain = build_chain(snaps)
    assert chain.total_added() == 2


def test_total_removed():
    snaps = [
        _snap("v1", {"A": "1", "B": "2"}),
        _snap("v2", {"A": "1"}),
        _snap("v3", {}),
    ]
    chain = build_chain(snaps)
    assert chain.total_removed() == 2


def test_chain_summary_empty():
    chain = DiffChain(links=[])
    assert "No transitions" in chain_summary(chain)


def test_chain_summary_shows_labels():
    snaps = [
        _snap("prod", {"X": "1"}),
        _snap("staging", {"X": "2"}),
    ]
    chain = build_chain(snaps)
    summary = chain_summary(chain)
    assert "prod" in summary
    assert "staging" in summary


def test_chain_link_repr():
    snaps = [
        _snap("a", {"K": "v"}),
        _snap("b", {}),
    ]
    chain = build_chain(snaps)
    r = repr(chain.links[0])
    assert "ChainLink" in r
    assert "a" in r
