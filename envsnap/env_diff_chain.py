"""Chain multiple snapshots into a sequential diff series."""
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from envsnap.diff import compare, DiffResult


@dataclass
class ChainLink:
    index: int
    label_from: str
    label_to: str
    result: DiffResult

    def __repr__(self) -> str:
        return (
            f"ChainLink({self.index}: {self.label_from!r} -> {self.label_to!r}, "
            f"added={len(self.result.added)}, removed={len(self.result.removed)}, "
            f"changed={len(self.result.changed)})"
        )


@dataclass
class DiffChain:
    links: List[ChainLink] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.links)

    def total_added(self) -> int:
        return sum(len(l.result.added) for l in self.links)

    def total_removed(self) -> int:
        return sum(len(l.result.removed) for l in self.links)

    def total_changed(self) -> int:
        return sum(len(l.result.changed) for l in self.links)


def build_chain(snapshots: List[Dict]) -> DiffChain:
    """Build a diff chain from an ordered list of snapshots."""
    if len(snapshots) < 2:
        return DiffChain(links=[])
    links = []
    for i in range(len(snapshots) - 1):
        a = snapshots[i]
        b = snapshots[i + 1]
        result = compare(a, b)
        links.append(ChainLink(
            index=i,
            label_from=a.get("label", f"snap-{i}"),
            label_to=b.get("label", f"snap-{i+1}"),
            result=result,
        ))
    return DiffChain(links=links)


def chain_summary(chain: DiffChain) -> str:
    if not chain.links:
        return "No transitions in chain."
    lines = [f"Chain of {len(chain)} transition(s):"]
    for link in chain.links:
        lines.append(
            f"  [{link.index}] {link.label_from} -> {link.label_to}: "
            f"+{len(link.result.added)} -{len(link.result.removed)} ~{len(link.result.changed)}"
        )
    lines.append(
        f"Total: +{chain.total_added()} -{chain.total_removed()} ~{chain.total_changed()}"
    )
    return "\n".join(lines)
