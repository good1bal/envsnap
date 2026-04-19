import pytest
from envsnap.env_patch import (
    PatchOperation,
    PatchResult,
    PatchError,
    apply_patch,
    patch_summary,
)


def _snap(**kwargs):
    return dict(kwargs)


def test_apply_patch_set_new_key():
    snap = _snap(FOO="bar")
    ops = [PatchOperation(op="set", key="BAZ", value="qux")]
    result = apply_patch(snap, ops)
    assert result.patched["BAZ"] == "qux"
    assert result.patched["FOO"] == "bar"


def test_apply_patch_set_overwrites_existing():
    snap = _snap(FOO="old")
    ops = [PatchOperation(op="set", key="FOO", value="new")]
    result = apply_patch(snap, ops)
    assert result.patched["FOO"] == "new"


def test_apply_patch_delete_existing_key():
    snap = _snap(FOO="bar", BAZ="qux")
    ops = [PatchOperation(op="delete", key="FOO")]
    result = apply_patch(snap, ops)
    assert "FOO" not in result.patched
    assert "BAZ" in result.patched


def test_apply_patch_delete_missing_key_skips():
    snap = _snap(FOO="bar")
    ops = [PatchOperation(op="delete", key="MISSING")]
    result = apply_patch(snap, ops)
    assert len(result.skipped) == 1
    assert len(result.applied) == 0


def test_apply_patch_delete_missing_strict_raises():
    snap = _snap(FOO="bar")
    ops = [PatchOperation(op="delete", key="MISSING")]
    with pytest.raises(PatchError, match="key not found"):
        apply_patch(snap, ops, strict=True)


def test_apply_patch_rename_key():
    snap = _snap(OLD="value")
    ops = [PatchOperation(op="rename", key="OLD", new_key="NEW")]
    result = apply_patch(snap, ops)
    assert "OLD" not in result.patched
    assert result.patched["NEW"] == "value"


def test_apply_patch_rename_missing_key_skips():
    snap = _snap(FOO="bar")
    ops = [PatchOperation(op="rename", key="MISSING", new_key="NEW")]
    result = apply_patch(snap, ops)
    assert len(result.skipped) == 1


def test_apply_patch_rename_conflict_strict_raises():
    snap = _snap(A="1", B="2")
    ops = [PatchOperation(op="rename", key="A", new_key="B")]
    with pytest.raises(PatchError, match="already exists"):
        apply_patch(snap, ops, strict=True)


def test_apply_patch_unknown_op_raises():
    snap = _snap(FOO="bar")
    ops = [PatchOperation(op="explode", key="FOO")]
    with pytest.raises(PatchError, match="Unknown operation"):
        apply_patch(snap, ops)


def test_apply_patch_original_unchanged():
    snap = _snap(FOO="bar")
    ops = [PatchOperation(op="set", key="FOO", value="new")]
    result = apply_patch(snap, ops)
    assert result.original["FOO"] == "bar"


def test_patch_summary_contains_counts():
    snap = _snap(FOO="bar")
    ops = [
        PatchOperation(op="set", key="NEW", value="v"),
        PatchOperation(op="delete", key="MISSING"),
    ]
    result = apply_patch(snap, ops)
    summary = patch_summary(result)
    assert "Applied: 1" in summary
    assert "Skipped: 1" in summary
