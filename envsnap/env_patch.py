"""Apply a patch (set of changes) to a snapshot."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PatchOperation:
    op: str  # 'set', 'delete', 'rename'
    key: str
    value: Optional[str] = None
    new_key: Optional[str] = None

    def __repr__(self) -> str:
        if self.op == "set":
            return f"PatchOperation(set {self.key}={self.value!r})"
        if self.op == "delete":
            return f"PatchOperation(delete {self.key})"
        return f"PatchOperation(rename {self.key}->{self.new_key})"


@dataclass
class PatchResult:
    original: Dict[str, str]
    patched: Dict[str, str]
    applied: List[PatchOperation] = field(default_factory=list)
    skipped: List[PatchOperation] = field(default_factory=list)


class PatchError(Exception):
    pass


def apply_patch(
    snapshot: Dict[str, str],
    operations: List[PatchOperation],
    strict: bool = False,
) -> PatchResult:
    """Apply a list of patch operations to a snapshot dict."""
    result = dict(snapshot)
    applied: List[PatchOperation] = []
    skipped: List[PatchOperation] = []

    for op in operations:
        if op.op == "set":
            result[op.key] = op.value or ""
            applied.append(op)
        elif op.op == "delete":
            if op.key in result:
                del result[op.key]
                applied.append(op)
            else:
                if strict:
                    raise PatchError(f"delete: key not found: {op.key!r}")
                skipped.append(op)
        elif op.op == "rename":
            if op.key not in result:
                if strict:
                    raise PatchError(f"rename: key not found: {op.key!r}")
                skipped.append(op)
            elif op.new_key in result and strict:
                raise PatchError(f"rename: target key already exists: {op.new_key!r}")
            else:
                result[op.new_key] = result.pop(op.key)
                applied.append(op)
        else:
            raise PatchError(f"Unknown operation: {op.op!r}")

    return PatchResult(original=snapshot, patched=result, applied=applied, skipped=skipped)


def patch_summary(result: PatchResult) -> str:
    lines = [
        f"Applied: {len(result.applied)}  Skipped: {len(result.skipped)}",
    ]
    for op in result.applied:
        lines.append(f"  [ok]   {op}")
    for op in result.skipped:
        lines.append(f"  [skip] {op}")
    return "\n".join(lines)
