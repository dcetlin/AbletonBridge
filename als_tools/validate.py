"""Structural checks for a Live set (.als).

    als-validate set.als [more.als ...]     # exit 1 if any set has problems
"""

from __future__ import annotations

import sys
from collections import Counter
from dataclasses import dataclass, field
from xml.etree.ElementTree import Element

from als_tools import liveset as ls


@dataclass(frozen=True)
class Report:
    pointee_count: int
    duplicate_pointee_ids: list[str] = field(default_factory=list[str])
    pointee_ids_not_below_next: list[str] = field(default_factory=list[str])
    duplicate_track_ids: list[str] = field(default_factory=list[str])
    dangling_pointee_refs: list[str] = field(default_factory=list[str])
    duplicate_lom_ids: list[str] = field(default_factory=list[str])
    unresolved_mappings: list[str] = field(default_factory=list[str])

    @property
    def problems(self) -> dict[str, list[str]]:
        return {k: v for k, v in vars(self).items() if isinstance(v, list) and v}

    @property
    def ok(self) -> bool:
        return not self.problems


def validate(root: Element) -> Report:
    """Check that ids are unique and every reference resolves."""
    next_id = ls.to_int(ls.value(root, "LiveSet/NextPointeeId"), "NextPointeeId")
    ids = Counter(ls.attr(e, "Id") for e in ls.pointees(root))
    track_ids = Counter(ls.attr(t, "Id") for t in ls.tracks(root))
    refs = {ls.attr(e, "Value") for e in root.iter("PointeeId")} - {"0"}
    loms = Counter(ls.attr(e, "Value") for e in ls.lom_definitions(root))
    mapped = {ls.value(r, "LomId") for r in root.iter("MxDIdRef")} - {"0"}
    return Report(
        pointee_count=len(ids),
        duplicate_pointee_ids=sorted(k for k, n in ids.items() if n > 1),
        pointee_ids_not_below_next=sorted(k for k in ids if ls.to_int(k, "pointee Id") >= next_id),
        duplicate_track_ids=sorted(k for k, n in track_ids.items() if n > 1),
        dangling_pointee_refs=sorted(r for r in refs if r not in ids),
        duplicate_lom_ids=sorted(k for k, n in loms.items() if n > 1),
        unresolved_mappings=sorted(m for m in mapped if m not in loms),
    )


def main(argv: list[str] | None = None) -> int:
    paths = sys.argv[1:] if argv is None else argv
    if not paths:
        print("usage: als-validate set.als [more.als ...]", file=sys.stderr)
        return 2
    failed = False
    for path in paths:
        try:
            report = validate(ls.read_set(path))
        except ls.AlsError as e:
            failed = True
            print(f"FAIL  {path}: {e}")
            continue
        if report.ok:
            print(f"ok    {path} ({report.pointee_count} pointees)")
        else:
            failed = True
            print(f"FAIL  {path}")
            for name, items in report.problems.items():
                print(f"      {name}: {items[:10]}{' ...' if len(items) > 10 else ''}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
