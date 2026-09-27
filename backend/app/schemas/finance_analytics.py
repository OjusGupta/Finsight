from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict


# ── Run Summary ──────────────────────────────────────────────────────────────

class RunSummaryResponse(BaseModel):
    run_id: int
    source_system: str
    status: str
    run_started_at: datetime
    run_completed_at: datetime | None = None
    lines_read: int
    lines_valid: int
    lines_rejected: int
    duplicate_lines_skipped: int
    invoices_processed: int
    invoices_reconciled: int
    invoices_blocked: int
    amount_reconciled: Decimal
    amount_blocked: Decimal
    reconciliation_rate_pct: float
    posting_success_rate_pct: float | None = None

    model_config = ConfigDict(from_attributes=True)


# ── Reconciliation State Counts ──────────────────────────────────────────────

class StateCountItem(BaseModel):
    finance_state: str
    line_count: int
    total_amount: Decimal


class StateCountsResponse(BaseModel):
    run_id: int
    states: list[StateCountItem]


# ── Reconciliation Status by Store ───────────────────────────────────────────

class StoreStateItem(BaseModel):
    store_id: int | None
    store_name: str | None
    finance_state: str
    line_count: int
    total_amount: Decimal


class StoreStatesResponse(BaseModel):
    run_id: int
    stores: list[StoreStateItem]


# ── Reconciled Sales by Store / Date ─────────────────────────────────────────

class ReconciledSalesItem(BaseModel):
    store_id: int | None
    store_name: str | None
    transaction_date: date
    invoices_reconciled: int
    reconciled_amount: Decimal


class ReconciledSalesResponse(BaseModel):
    run_id: int
    rows: list[ReconciledSalesItem]


# ── Blocked Documents ────────────────────────────────────────────────────────

class BlockedDocumentItem(BaseModel):
    finance_line_id: int
    invoice_no: str
    finance_state: str
    rejection_reason: str | None
    line_total: Decimal
    return_id: int | None
    sale_id: int | None
    store_id: int | None
    product_id: int | None
    transaction_date: date


class BlockedDocumentsResponse(BaseModel):
    run_id: int
    blocked_count: int
    documents: list[BlockedDocumentItem]


# ── Posting Counts ───────────────────────────────────────────────────────────

class PostingCountItem(BaseModel):
    posting_status: str
    invoice_count: int
    total_attempts: int


class PostingCountsResponse(BaseModel):
    run_id: int
    totals: list[PostingCountItem]


# ── Posting Status by Invoice ────────────────────────────────────────────────

class PostingInvoiceItem(BaseModel):
    invoice_no: str
    doc_type: str
    posting_status: str
    attempt_count: int
    last_http_status: int | None
    last_result: str | None
    timeout_observed: bool
    external_document_id: str | None
    last_error: str | None
    first_attempt_at: datetime | None
    last_attempt_at: datetime | None
    posted_at: datetime | None


class PostingInvoicesResponse(BaseModel):
    run_id: int
    invoices: list[PostingInvoiceItem]


# ── Posting Failures and Retries ─────────────────────────────────────────────

class PostingFailureItem(BaseModel):
    invoice_no: str
    doc_type: str
    posting_status: str
    attempt_count: int
    last_http_status: int | None
    timeout_observed: bool
    last_error: str | None
    last_attempt_at: datetime | None


class PostingFailuresResponse(BaseModel):
    run_id: int
    failure_count: int
    failures: list[PostingFailureItem]


# ── Finance Anomaly Summary ───────────────────────────────────────────────────

class AnomalySummaryItem(BaseModel):
    anomaly_type: str
    severity: str
    anomaly_count: int
    status: str


class AnomalySummaryResponse(BaseModel):
    run_id: int | None
    anomalies: list[AnomalySummaryItem]


# ── All Anomaly Types (cross-phase) ──────────────────────────────────────────

class AllAnomalyTypeItem(BaseModel):
    anomaly_type: str
    severity: str
    anomaly_count: int
    status: str


class AllAnomalyTypesResponse(BaseModel):
    anomaly_types: list[AllAnomalyTypeItem]


# ── Latest Run (lightweight) ─────────────────────────────────────────────────

class LatestRunResponse(BaseModel):
    run_id: int
    source_system: str
    status: str
    invoices_reconciled: int
    invoices_blocked: int
    amount_reconciled: Decimal
    amount_blocked: Decimal
    run_started_at: datetime
    run_completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
