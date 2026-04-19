import pytest
from envsnap.env_copy import copy_key, copy_keys, clone_snapshot, copy_summary, CopyConflict


def _snap(env: dict, label: str = "test") -> dict:
    return {"label": label, "env": env, "meta": {}}


def test_copy_key_basic():
    snap = _snap({"A": "1", "B": "2"})
    result = copy_key(snap, "A", "A_COPY")
    assert result["env"]["A_COPY"] == "1"
    assert result["env"]["A"] == "1"


def test_copy_key_preserves_original():
    snap = _snap({"A": "1"})
    result = copy_key(snap, "A", "A2")
    assert "A" in result["env"]


def test_copy_key_missing_src_raises():
    snap = _snap({"A": "1"})
    with pytest.raises(KeyError):
        copy_key(snap, "MISSING", "DST")


def test_copy_key_conflict_raises():
    snap = _snap({"A": "1", "B": "2"})
    with pytest.raises(CopyConflict):
        copy_key(snap, "A", "B")


def test_copy_key_overwrite():
    snap = _snap({"A": "1", "B": "old"})
    result = copy_key(snap, "A", "B", overwrite=True)
    assert result["env"]["B"] == "1"


def test_copy_keys_multiple():
    snap = _snap({"X": "10", "Y": "20"})
    result = copy_keys(snap, {"X": "X2", "Y": "Y2"})
    assert result["env"]["X2"] == "10"
    assert result["env"]["Y2"] == "20"


def test_copy_keys_conflict_raises():
    snap = _snap({"X": "1", "Y": "2"})
    with pytest.raises(CopyConflict):
        copy_keys(snap, {"X": "Y"})


def test_clone_snapshot_label():
    snap = _snap({"A": "1"}, label="original")
    result = clone_snapshot(snap, label="cloned")
    assert result["label"] == "cloned"
    assert result["env"] == {"A": "1"}


def test_clone_snapshot_prefix_strip():
    snap = _snap({"APP_HOST": "localhost", "APP_PORT": "8080"})
    result = clone_snapshot(snap, prefix_strip="APP_")
    assert "HOST" in result["env"]
    assert "PORT" in result["env"]
    assert "APP_HOST" not in result["env"]


def test_clone_snapshot_prefix_add():
    snap = _snap({"HOST": "localhost"})
    result = clone_snapshot(snap, prefix_add="SVC_")
    assert "SVC_HOST" in result["env"]


def test_clone_snapshot_strip_and_add():
    snap = _snap({"OLD_KEY": "val"})
    result = clone_snapshot(snap, prefix_strip="OLD_", prefix_add="NEW_")
    assert "NEW_KEY" in result["env"]
    assert result["env"]["NEW_KEY"] == "val"


def test_copy_summary_counts_new_keys():
    snap = _snap({"A": "1"})
    result = copy_key(snap, "A", "A_COPY")
    summary = copy_summary(snap, result)
    assert "1" in summary
    assert "A_COPY" in summary
