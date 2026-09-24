from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class PostingJournal:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.entries = self._load()

    def _load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"cannot load journal: {self.path}") from exc
        if not isinstance(value, list):
            raise RuntimeError(f"journal must contain an array: {self.path}")
        return value

    def record(self, invoice_no: str, attempt: int, **result: Any) -> None:
        self.entries.append(
            {
                "invoice_no": invoice_no,
                "attempt": attempt,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                **result,
            }
        )
        self._save()

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        payload = json.dumps(self.entries, indent=2, sort_keys=True)
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, self.path)
