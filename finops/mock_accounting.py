from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from .models import AccountingResponse, AccountingTimeout


class MockAccountingClient:
    """Deterministic local accounting API substitute for tests and live validation."""

    def __init__(self, behavior: Callable[[int, Mapping[str, Any]], Any] | None = None):
        self.behavior = behavior
        self.calls: list[tuple[str, Mapping[str, Any]]] = []

    def post(self, document: Mapping[str, Any], idempotency_key: str) -> AccountingResponse:
        self.calls.append((idempotency_key, document))
        attempt = sum(1 for key, _ in self.calls if key == idempotency_key)
        if self.behavior is None:
            return AccountingResponse(201, f"mock-{idempotency_key}")
        result = self.behavior(attempt, document)
        if isinstance(result, BaseException):
            raise result
        return result
