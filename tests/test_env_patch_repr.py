from envsnap.env_patch import PatchOperation, PatchResult, patch_summary


def test_repr_set():
    op = PatchOperation(op="set", key="FOO", value="bar")
    assert "set" in repr(op)
    assert "FOO" in repr(op)


def test_repr_delete():
    op = PatchOperation(op="delete", key="FOO")
    assert "delete" in repr(op)


def test_repr_rename():
    op = PatchOperation(op="rename", key="OLD", new_key="NEW")
    assert "OLD" in repr(op)
    assert "NEW" in repr(op)


def test_patch_result_fields():
    orig = {"A": "1"}
    patched = {"A": "2"}
    op = PatchOperation(op="set", key="A", value="2")
    result = PatchResult(original=orig, patched=patched, applied=[op], skipped=[])
    assert result.original is orig
    assert result.patched is patched
    assert len(result.applied) == 1


def test_patch_summary_ok_and_skip_labels():
    orig = {"A": "1"}
    applied_op = PatchOperation(op="set", key="A", value="2")
    skipped_op = PatchOperation(op="delete", key="MISSING")
    result = PatchResult(
        original=orig,
        patched={"A": "2"},
        applied=[applied_op],
        skipped=[skipped_op],
    )
    summary = patch_summary(result)
    assert "[ok]" in summary
    assert "[skip]" in summary


def test_patch_summary_empty_ops():
    result = PatchResult(original={}, patched={}, applied=[], skipped=[])
    summary = patch_summary(result)
    assert "Applied: 0" in summary
    assert "Skipped: 0" in summary
