from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.models.accounting_posting import AccountingPosting
from backend.app.models.anomaly import Anomaly
from backend.app.models.finance_reconciliation_line import FinanceReconciliationLine
from backend.app.models.finance_reconciliation_run import FinanceReconciliationRun
from backend.app.models.store import Store
from backend.app.schemas.finance_analytics import (
    AllAnomalyTypeItem,
    AllAnomalyTypesResponse,
    AnomalySummaryItem,
    AnomalySummaryResponse,
    BlockedDocumentItem,
    BlockedDocumentsResponse,
    LatestRunResponse,
    PostingCountItem,
    PostingCountsResponse,
    PostingFailureItem,
    PostingFailuresResponse,
    PostingInvoiceItem,
    PostingInvoicesResponse,
    ReconciledSalesItem,
    ReconciledSalesResponse,
    RunSummaryResponse,
    StateCountItem,
    StateCountsResponse,
    StoreStateItem,
    StoreStatesResponse,
)


def _run_or_none(db: Session, run_id: int) -> FinanceReconciliationRun | None:
    return (
        db.query(FinanceReconciliationRun)
        .filter(FinanceReconciliationRun.run_id == run_id)
        .first()
    )


def _posting_success_rate(db: Session, run_id: int) -> float | None:
    rows = (
        db.query(AccountingPosting.posting_status, func.count().label("cnt"))
        .filter(AccountingPosting.run_id == run_id)
        .group_by(AccountingPosting.posting_status)
        .all()
    )
    if not rows:
        return None
    total = sum(r.cnt for r in rows)
    success = sum(
        r.cnt for r in rows
        if r.posting_status in ("POSTED", "ALREADY_POSTED")
    )
    return round(success / total * 100, 2) if total else None


# ── 1. Run Summary ───────────────────────────────────────────────────────────

def get_run_summary(db: Session, run_id: int) -> RunSummaryResponse | None:
    run = _run_or_none(db, run_id)
    if run is None:
        return None
    recon_rate = (
        round(run.invoices_reconciled / run.invoices_processed * 100, 2)
        if run.invoices_processed
        else 0.0
    )
    return RunSummaryResponse(
        run_id=run.run_id,
        source_system=run.source_system,
        status=run.status,
        run_started_at=run.run_started_at,
        run_completed_at=run.run_completed_at,
        lines_read=run.lines_read,
        lines_valid=run.lines_valid,
        lines_rejected=run.lines_rejected,
        duplicate_lines_skipped=run.duplicate_lines_skipped,
        invoices_processed=run.invoices_processed,
        invoices_reconciled=run.invoices_reconciled,
        invoices_blocked=run.invoices_blocked,
        amount_reconciled=run.amount_reconciled,
        amount_blocked=run.amount_blocked,
        reconciliation_rate_pct=recon_rate,
        posting_success_rate_pct=_posting_success_rate(db, run_id),
    )


# ── 2. Reconciliation State Counts ───────────────────────────────────────────

def get_state_counts(db: Session, run_id: int) -> StateCountsResponse | None:
    if _run_or_none(db, run_id) is None:
        return None
    rows = (
        db.query(
            FinanceReconciliationLine.finance_state,
            func.count().label("line_count"),
            func.coalesce(func.sum(FinanceReconciliationLine.line_total), 0).label("total_amount"),
        )
        .filter(FinanceReconciliationLine.run_id == run_id)
        .group_by(FinanceReconciliationLine.finance_state)
        .order_by(FinanceReconciliationLine.finance_state)
        .all()
    )
    return StateCountsResponse(
        run_id=run_id,
        states=[
            StateCountItem(
                finance_state=r.finance_state,
                line_count=r.line_count,
                total_amount=Decimal(str(r.total_amount)),
            )
            for r in rows
        ],
    )


# ── 3. Reconciliation Status by Store ────────────────────────────────────────

def get_store_states(db: Session, run_id: int) -> StoreStatesResponse | None:
    if _run_or_none(db, run_id) is None:
        return None
    rows = (
        db.query(
            FinanceReconciliationLine.store_id,
            Store.store_name,
            FinanceReconciliationLine.finance_state,
            func.count().label("line_count"),
            func.coalesce(func.sum(FinanceReconciliationLine.line_total), 0).label("total_amount"),
        )
        .outerjoin(Store, Store.store_id == FinanceReconciliationLine.store_id)
        .filter(FinanceReconciliationLine.run_id == run_id)
        .group_by(
            FinanceReconciliationLine.store_id,
            Store.store_name,
            FinanceReconciliationLine.finance_state,
        )
        .order_by(FinanceReconciliationLine.store_id, FinanceReconciliationLine.finance_state)
        .all()
    )
    return StoreStatesResponse(
        run_id=run_id,
        stores=[
            StoreStateItem(
                store_id=r.store_id,
                store_name=r.store_name,
                finance_state=r.finance_state,
                line_count=r.line_count,
                total_amount=Decimal(str(r.total_amount)),
            )
            for r in rows
        ],
    )


# ── 4. Reconciled Sales by Store / Date ──────────────────────────────────────

def get_reconciled_sales(db: Session, run_id: int) -> ReconciledSalesResponse | None:
    if _run_or_none(db, run_id) is None:
        return None
    rows = (
        db.query(
            FinanceReconciliationLine.store_id,
            Store.store_name,
            FinanceReconciliationLine.transaction_date,
            func.count(func.distinct(FinanceReconciliationLine.invoice_no)).label("invoices_reconciled"),
            func.coalesce(func.sum(FinanceReconciliationLine.line_total), 0).label("reconciled_amount"),
        )
        .outerjoin(Store, Store.store_id == FinanceReconciliationLine.store_id)
        .filter(
            FinanceReconciliationLine.run_id == run_id,
            FinanceReconciliationLine.finance_state == "RECONCILED",
            FinanceReconciliationLine.doc_type == "sale",
        )
        .group_by(
            FinanceReconciliationLine.store_id,
            Store.store_name,
            FinanceReconciliationLine.transaction_date,
        )
        .order_by(FinanceReconciliationLine.store_id, FinanceReconciliationLine.transaction_date)
        .all()
    )
    return ReconciledSalesResponse(
        run_id=run_id,
        rows=[
            ReconciledSalesItem(
                store_id=r.store_id,
                store_name=r.store_name,
                transaction_date=r.transaction_date,
                invoices_reconciled=r.invoices_reconciled,
                reconciled_amount=Decimal(str(r.reconciled_amount)),
            )
            for r in rows
        ],
    )


# ── 5. Blocked Documents ─────────────────────────────────────────────────────

def get_blocked_documents(db: Session, run_id: int) -> BlockedDocumentsResponse | None:
    if _run_or_none(db, run_id) is None:
        return None
    rows = (
        db.query(FinanceReconciliationLine)
        .filter(
            FinanceReconciliationLine.run_id == run_id,
            FinanceReconciliationLine.doc_type == "sales_return",
            FinanceReconciliationLine.finance_state != "RECONCILED",
        )
        .order_by(FinanceReconciliationLine.finance_line_id)
        .all()
    )
    return BlockedDocumentsResponse(
        run_id=run_id,
        blocked_count=len(rows),
        documents=[
            BlockedDocumentItem(
                finance_line_id=r.finance_line_id,
                invoice_no=r.invoice_no,
                finance_state=r.finance_state,
                rejection_reason=r.rejection_reason,
                line_total=r.line_total,
                return_id=r.return_id,
                sale_id=r.sale_id,
                store_id=r.store_id,
                product_id=r.product_id,
                transaction_date=r.transaction_date,
            )
            for r in rows
        ],
    )


# ── 6. Posting Counts ────────────────────────────────────────────────────────

def get_posting_counts(db: Session, run_id: int) -> PostingCountsResponse | None:
    if _run_or_none(db, run_id) is None:
        return None
    rows = (
        db.query(
            AccountingPosting.posting_status,
            func.count().label("invoice_count"),
            func.coalesce(func.sum(AccountingPosting.attempt_count), 0).label("total_attempts"),
        )
        .filter(AccountingPosting.run_id == run_id)
        .group_by(AccountingPosting.posting_status)
        .order_by(AccountingPosting.posting_status)
        .all()
    )
    return PostingCountsResponse(
        run_id=run_id,
        totals=[
            PostingCountItem(
                posting_status=r.posting_status,
                invoice_count=r.invoice_count,
                total_attempts=int(r.total_attempts),
            )
            for r in rows
        ],
    )


# ── 7. Posting Status by Invoice ─────────────────────────────────────────────

def get_posting_invoices(db: Session, run_id: int) -> PostingInvoicesResponse | None:
    if _run_or_none(db, run_id) is None:
        return None
    rows = (
        db.query(AccountingPosting)
        .filter(AccountingPosting.run_id == run_id)
        .order_by(AccountingPosting.invoice_no)
        .all()
    )
    return PostingInvoicesResponse(
        run_id=run_id,
        invoices=[
            PostingInvoiceItem(
                invoice_no=r.invoice_no,
                doc_type=r.doc_type,
                posting_status=r.posting_status,
                attempt_count=r.attempt_count,
                last_http_status=r.last_http_status,
                last_result=r.last_result,
                timeout_observed=r.timeout_observed,
                external_document_id=r.external_document_id,
                last_error=r.last_error,
                first_attempt_at=r.first_attempt_at,
                last_attempt_at=r.last_attempt_at,
                posted_at=r.posted_at,
            )
            for r in rows
        ],
    )


# ── 8. Posting Failures and Retries ──────────────────────────────────────────

def get_posting_failures(db: Session, run_id: int) -> PostingFailuresResponse | None:
    if _run_or_none(db, run_id) is None:
        return None
    rows = (
        db.query(AccountingPosting)
        .filter(
            AccountingPosting.run_id == run_id,
            (
                AccountingPosting.posting_status.in_(
                    ["FAILED", "PERMANENT_FAILURE", "RETRYABLE_FAILURE", "TIMEOUT"]
                )
                | (AccountingPosting.attempt_count > 1)
            ),
        )
        .order_by(AccountingPosting.attempt_count.desc(), AccountingPosting.invoice_no)
        .all()
    )
    return PostingFailuresResponse(
        run_id=run_id,
        failure_count=len(rows),
        failures=[
            PostingFailureItem(
                invoice_no=r.invoice_no,
                doc_type=r.doc_type,
                posting_status=r.posting_status,
                attempt_count=r.attempt_count,
                last_http_status=r.last_http_status,
                timeout_observed=r.timeout_observed,
                last_error=r.last_error,
                last_attempt_at=r.last_attempt_at,
            )
            for r in rows
        ],
    )


# ── 9. Finance Anomaly Summary ────────────────────────────────────────────────

def get_finance_anomaly_summary(db: Session, run_id: int) -> AnomalySummaryResponse | None:
    if _run_or_none(db, run_id) is None:
        return None
    rows = (
        db.query(
            Anomaly.anomaly_type,
            Anomaly.severity,
            func.count().label("anomaly_count"),
            Anomaly.status,
        )
        .filter(
            Anomaly.anomaly_type.like("FINANCE_%")
            | Anomaly.anomaly_type.like("ACCOUNTING_POSTING_%")
        )
        .group_by(Anomaly.anomaly_type, Anomaly.severity, Anomaly.status)
        .order_by(Anomaly.anomaly_type, Anomaly.severity)
        .all()
    )
    return AnomalySummaryResponse(
        run_id=run_id,
        anomalies=[
            AnomalySummaryItem(
                anomaly_type=r.anomaly_type,
                severity=r.severity,
                anomaly_count=r.anomaly_count,
                status=r.status,
            )
            for r in rows
        ],
    )


# ── 10. All Anomaly Types (cross-phase) ───────────────────────────────────────

def get_all_anomaly_types(db: Session) -> AllAnomalyTypesResponse:
    rows = (
        db.query(
            Anomaly.anomaly_type,
            Anomaly.severity,
            func.count().label("anomaly_count"),
            Anomaly.status,
        )
        .group_by(Anomaly.anomaly_type, Anomaly.severity, Anomaly.status)
        .order_by(Anomaly.anomaly_type, Anomaly.severity)
        .all()
    )
    return AllAnomalyTypesResponse(
        anomaly_types=[
            AllAnomalyTypeItem(
                anomaly_type=r.anomaly_type,
                severity=r.severity,
                anomaly_count=r.anomaly_count,
                status=r.status,
            )
            for r in rows
        ]
    )


# ── 11. Latest Run (lightweight) ─────────────────────────────────────────────

def get_latest_run_summary(db: Session) -> LatestRunResponse | None:
    run = (
        db.query(FinanceReconciliationRun)
        .order_by(
            FinanceReconciliationRun.run_started_at.desc(),
            FinanceReconciliationRun.run_id.desc(),
        )
        .first()
    )
    if run is None:
        return None
    return LatestRunResponse(
        run_id=run.run_id,
        source_system=run.source_system,
        status=run.status,
        invoices_reconciled=run.invoices_reconciled,
        invoices_blocked=run.invoices_blocked,
        amount_reconciled=run.amount_reconciled,
        amount_blocked=run.amount_blocked,
        run_started_at=run.run_started_at,
        run_completed_at=run.run_completed_at,
    )
