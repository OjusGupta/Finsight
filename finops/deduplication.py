from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .models import LineReject


@dataclass(frozen=True)
class DeduplicationResult:
    rows: tuple[Mapping[str, Any], ...]
    rejects: tuple[LineReject, ...]
    duplicate_lines_skipped: int
    conflicting_invoices: frozenset[str]


def deduplicate_lines(rows: list[Mapping[str, Any]]) -> DeduplicationResult:
    groups: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for row in rows:
        key = (str(row.get("invoice_no", "")).strip(), str(row.get("line_no", "")).strip())
        groups.setdefault(key, []).append(row)

    kept: list[Mapping[str, Any]] = []
    rejects: list[LineReject] = []
    skipped = 0
    conflicting_invoices: set[str] = set()

    for (invoice_no, line_no), group in groups.items():
        if len(group) == 1:
            kept.append(group[0])
            continue
        if all(dict(row) == dict(group[0]) for row in group[1:]):
            kept.append(group[0])
            skipped += len(group) - 1
            continue
        conflicting_invoices.add(invoice_no)
        rejects.extend(
            LineReject(invoice_no, line_no, "conflicting_duplicate")
            for _ in group
        )

    return DeduplicationResult(
        tuple(kept), tuple(rejects), skipped, frozenset(conflicting_invoices)
    )
