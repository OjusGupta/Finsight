from sqlalchemy.orm import Session

from backend.app.models.accounting_posting import AccountingPosting
from backend.app.models.anomaly import Anomaly
from backend.app.models.finance_reconciliation_line import FinanceReconciliationLine
from backend.app.models.finance_reconciliation_run import FinanceReconciliationRun


# ── Reconciliation Runs ──────────────────────────────────────────────────────

def get_all_runs(db: Session) -> list[FinanceReconciliationRun]:
    return (
        db.query(FinanceReconciliationRun)
        .order_by(FinanceReconciliationRun.run_started_at.desc())
        .all()
    )


def get_run_by_id(db: Session, run_id: int) -> FinanceReconciliationRun | None:
    return (
        db.query(FinanceReconciliationRun)
        .filter(FinanceReconciliationRun.run_id == run_id)
        .first()
    )


def get_latest_run(db: Session) -> FinanceReconciliationRun | None:
    return (
        db.query(FinanceReconciliationRun)
        .order_by(
            FinanceReconciliationRun.run_started_at.desc(),
            FinanceReconciliationRun.run_id.desc(),
        )
        .first()
    )


# ── Reconciliation Lines ─────────────────────────────────────────────────────

def get_all_lines(db: Session) -> list[FinanceReconciliationLine]:
    return (
        db.query(FinanceReconciliationLine)
        .order_by(FinanceReconciliationLine.finance_line_id)
        .all()
    )


def get_lines_by_run(db: Session, run_id: int) -> list[FinanceReconciliationLine]:
    return (
        db.query(FinanceReconciliationLine)
        .filter(FinanceReconciliationLine.run_id == run_id)
        .order_by(FinanceReconciliationLine.finance_line_id)
        .all()
    )


# ── Accounting Postings ──────────────────────────────────────────────────────

def get_all_postings(db: Session) -> list[AccountingPosting]:
    return (
        db.query(AccountingPosting)
        .order_by(AccountingPosting.posting_id)
        .all()
    )


def get_postings_by_run(db: Session, run_id: int) -> list[AccountingPosting]:
    return (
        db.query(AccountingPosting)
        .filter(AccountingPosting.run_id == run_id)
        .order_by(AccountingPosting.invoice_no)
        .all()
    )


# ── Finance Anomalies ────────────────────────────────────────────────────────

def get_finance_anomalies(db: Session) -> list[Anomaly]:
    return (
        db.query(Anomaly)
        .filter(
            Anomaly.anomaly_type.like("FINANCE_%")
            | Anomaly.anomaly_type.like("ACCOUNTING_POSTING_%")
        )
        .order_by(Anomaly.anomaly_id)
        .all()
    )
