from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class PostedLedger:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.records = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"cannot load ledger: {self.path}") from exc
        if not isinstance(value, dict):
            raise RuntimeError(f"ledger must contain an object: {self.path}")
        return value

    def contains(self, invoice_no: str) -> bool:
        return invoice_no in self.records

    def record(self, invoice_no: str, document_id: str | None, outcome: str) -> None:
        self.records[invoice_no] = {
            "document_id": document_id,
            "outcome": outcome,
        }
        self._save()

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        payload = json.dumps(self.records, indent=2, sort_keys=True)
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, self.path)
