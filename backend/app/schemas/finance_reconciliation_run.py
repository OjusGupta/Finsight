from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict


class FinanceReconciliationRunResponse(BaseModel):
    run_id: int
    source_system: str
    run_started_at: datetime
    run_completed_at: datetime | None = None
    status: str
    lines_read: int
    lines_valid: int
    lines_rejected: int
    duplicate_lines_skipped: int
    invoices_processed: int
    invoices_reconciled: int
    invoices_blocked: int
    amount_reconciled: Decimal
    amount_blocked: Decimal
    summary_json: dict[str, Any] | None = None
    error_message: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
