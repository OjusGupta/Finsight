from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AccountingPostingResponse(BaseModel):
    posting_id: int
    run_id: int
    invoice_no: str
    doc_type: str
    idempotency_key: str
    reconciliation_state: str
    posting_status: str
    attempt_count: int
    external_document_id: str | None = None
    last_http_status: int | None = None
    last_result: str | None = None
    last_error: str | None = None
    timeout_observed: bool
    attempt_history: list[Any]
    first_attempt_at: datetime | None = None
    last_attempt_at: datetime | None = None
    posted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
