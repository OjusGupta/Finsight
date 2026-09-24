from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


class FinanceAnalytics:
    def __init__(self, connection: Any):
        self.connection = connection

    def latest_run_id(self) -> int | None:
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT run_id FROM finance_reconciliation_runs "
            "ORDER BY run_started_at DESC, run_id DESC LIMIT 1"
        )
        row = cursor.fetchone()
        return int(row[0]) if row else None

    def summary(self, run_id: int | None = None) -> dict[str, Any]:
        run_id = run_id if run_id is not None else self.latest_run_id()
        if run_id is None:
            return {"run_id": None, "run": None, "state_counts": [], "posting_counts": []}
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT run_id, source_system, status, lines_read, lines_valid,
                   lines_rejected, duplicate_lines_skipped, invoices_processed,
                   invoices_reconciled, invoices_blocked, amount_reconciled,
                   amount_blocked, run_started_at, run_completed_at
            FROM finance_reconciliation_runs
            WHERE run_id=%s
            """,
            (run_id,),
        )
        run = cursor.fetchone()
        cursor.execute(
            """
            SELECT finance_state, COUNT(*)
            FROM finance_reconciliation_lines
            WHERE run_id=%s
            GROUP BY finance_state
            ORDER BY finance_state
            """,
            (run_id,),
        )
        state_counts = cursor.fetchall()
        cursor.execute(
            """
            SELECT posting_status, COUNT(*), COALESCE(SUM(attempt_count), 0)
            FROM accounting_postings
            WHERE run_id=%s
            GROUP BY posting_status
            ORDER BY posting_status
            """,
            (run_id,),
        )
        posting_counts = cursor.fetchall()
        return {
            "run_id": run_id,
            "run": run,
            "state_counts": state_counts,
            "posting_counts": posting_counts,
        }

    def reconciliation_status_by_store(self, run_id: int | None = None) -> list[tuple[Any, ...]]:
        run_id = run_id if run_id is not None else self.latest_run_id()
        if run_id is None:
            return []
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT store_id, finance_state, COUNT(*),
                   COALESCE(SUM(line_total), 0)
            FROM finance_reconciliation_lines
            WHERE run_id=%s
            GROUP BY store_id, finance_state
            ORDER BY store_id, finance_state
            """,
            (run_id,),
        )
        return cursor.fetchall()

    def reconciled_sales_by_store_date(self, run_id: int | None = None) -> list[tuple[Any, ...]]:
        run_id = run_id if run_id is not None else self.latest_run_id()
        if run_id is None:
            return []
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT store_id, transaction_date, COUNT(DISTINCT invoice_no),
                   COALESCE(SUM(line_total), 0)
            FROM finance_reconciliation_lines
            WHERE run_id=%s AND finance_state='RECONCILED' AND doc_type='sale'
            GROUP BY store_id, transaction_date
            ORDER BY store_id, transaction_date
            """,
            (run_id,),
        )
        return cursor.fetchall()

    def blocked_returns(self, run_id: int | None = None) -> list[tuple[Any, ...]]:
        run_id = run_id if run_id is not None else self.latest_run_id()
        if run_id is None:
            return []
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT finance_line_id, invoice_no, return_id, return_item_id,
                   sale_id, store_id, product_id, finance_state, rejection_reason,
                   line_total
            FROM finance_reconciliation_lines
            WHERE run_id=%s AND doc_type='sales_return'
              AND finance_state <> 'RECONCILED'
            ORDER BY finance_line_id
            """,
            (run_id,),
        )
        return cursor.fetchall()

    def posting_success_failure_counts(self, run_id: int | None = None) -> list[tuple[Any, ...]]:
        run_id = run_id if run_id is not None else self.latest_run_id()
        if run_id is None:
            return []
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT posting_status, COUNT(*), COALESCE(SUM(attempt_count), 0)
            FROM accounting_postings
            WHERE run_id=%s
            GROUP BY posting_status
            ORDER BY posting_status
            """,
            (run_id,),
        )
        return cursor.fetchall()

    def posting_status_by_invoice(self, run_id: int | None = None) -> list[tuple[Any, ...]]:
        run_id = run_id if run_id is not None else self.latest_run_id()
        if run_id is None:
            return []
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT invoice_no, doc_type, idempotency_key, posting_status,
                   attempt_count, last_http_status, last_result,
                   timeout_observed, external_document_id, last_error
            FROM accounting_postings
            WHERE run_id=%s
            ORDER BY invoice_no
            """,
            (run_id,),
        )
        return cursor.fetchall()

    def finance_line_rows(self, run_id: int | None = None) -> list[dict[str, Any]]:
        run_id = run_id if run_id is not None else self.latest_run_id()
        if run_id is None:
            return []
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT finance_line_id, run_id, invoice_no, line_no, doc_type,
                   finance_state, rejection_reason, line_total, taxable_value,
                   gst_amount, company_id, store_id, customer_id, product_id,
                   sale_id, sale_item_id, return_id, return_item_id
            FROM finance_reconciliation_lines
            WHERE run_id=%s
            ORDER BY finance_line_id
            """,
            (run_id,),
        )
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def posting_rows(self, run_id: int | None = None) -> list[dict[str, Any]]:
        run_id = run_id if run_id is not None else self.latest_run_id()
        if run_id is None:
            return []
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT posting_id, run_id, invoice_no, doc_type, idempotency_key,
                   posting_status, attempt_count, last_http_status, last_result,
                   timeout_observed, external_document_id, last_error
            FROM accounting_postings
            WHERE run_id=%s
            ORDER BY posting_id
            """,
            (run_id,),
        )
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def report(self, run_id: int | None = None) -> dict[str, Any]:
        run_id = run_id if run_id is not None else self.latest_run_id()
        return {
            "summary": self.summary(run_id),
            "reconciliation_status_by_store": self.reconciliation_status_by_store(run_id),
            "reconciled_sales_by_store_date": self.reconciled_sales_by_store_date(run_id),
            "blocked_returns": self.blocked_returns(run_id),
            "posting_counts": self.posting_success_failure_counts(run_id),
            "posting_status_by_invoice": self.posting_status_by_invoice(run_id),
        }


def build_finance_anomaly_candidates(
    line_rows: Sequence[Mapping[str, Any]],
    posting_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    line_rules = {
        "TOTAL_MISMATCH": ("FINANCE_TOTAL_MISMATCH", "HIGH"),
        "FINANCE_FIELDS_INCOMPLETE": ("FINANCE_FIELDS_INCOMPLETE", "MEDIUM"),
        "CONFLICTING_DUPLICATE": ("FINANCE_CONFLICTING_DUPLICATE", "HIGH"),
        "INCOMPLETE_INVOICE": ("FINANCE_INCOMPLETE_INVOICE", "HIGH"),
    }
    for row in line_rows:
        state = row.get("finance_state")
        if state not in line_rules:
            continue
        anomaly_type, severity = line_rules[state]
        description = (
            f"{anomaly_type}|run_id={row.get('run_id')}"
            f"|finance_line_id={row.get('finance_line_id')}"
            f"|invoice_no={row.get('invoice_no')}"
            f"|line_no={row.get('line_no')}"
            f"|company_id={row.get('company_id')}"
            f"|store_id={row.get('store_id')}"
            f"|customer_id={row.get('customer_id')}"
            f"|product_id={row.get('product_id')}"
            f"|sale_id={row.get('sale_id')}"
            f"|sale_item_id={row.get('sale_item_id')}"
            f"|return_id={row.get('return_id')}"
            f"|return_item_id={row.get('return_item_id')}"
            f"|reason={row.get('rejection_reason')}"
        )
        candidates.append({
            "anomaly_type": anomaly_type,
            "severity": severity,
            "description": description,
            "store_id": row.get("store_id"),
            "product_id": row.get("product_id"),
            "sale_id": row.get("sale_id"),
            "detected_value": row.get("line_total"),
            "expected_value": None,
        })

    for row in posting_rows:
        status = row.get("posting_status")
        attempts = int(row.get("attempt_count") or 0)
        if status in {"FAILED", "PERMANENT_FAILURE", "RETRYABLE_FAILURE"}:
            anomaly_type, severity = "ACCOUNTING_POSTING_FAILURE", "HIGH"
        elif status == "TIMEOUT" or row.get("timeout_observed"):
            anomaly_type, severity = "ACCOUNTING_POSTING_TIMEOUT", "MEDIUM"
        elif attempts > 1:
            anomaly_type, severity = "ACCOUNTING_POSTING_RETRY", "MEDIUM"
        else:
            continue
        description = (
            f"{anomaly_type}|run_id={row.get('run_id')}"
            f"|posting_id={row.get('posting_id')}"
            f"|invoice_no={row.get('invoice_no')}"
            f"|idempotency_key={row.get('idempotency_key')}"
            f"|attempt_count={attempts}"
            f"|http_status={row.get('last_http_status')}"
            f"|last_error={row.get('last_error')}"
        )
        candidates.append({
            "anomaly_type": anomaly_type,
            "severity": severity,
            "description": description,
            "store_id": None,
            "product_id": None,
            "sale_id": None,
            "detected_value": attempts,
            "expected_value": 1,
        })
    return candidates


def persist_finance_anomalies(connection: Any, candidates: Sequence[Mapping[str, Any]]) -> int:
    cursor = connection.cursor()
    cursor.execute(
        "SELECT description FROM anomalies WHERE anomaly_type LIKE 'FINANCE_%' "
        "OR anomaly_type LIKE 'ACCOUNTING_POSTING_%'"
    )
    existing = {row[0] for row in cursor.fetchall()}
    inserted = 0
    for candidate in candidates:
        if candidate["description"] in existing:
            continue
        cursor.execute(
            """
            INSERT INTO anomalies (
                store_id, product_id, sale_id, anomaly_type, severity,
                description, detected_value, expected_value,
                detection_method, status
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'RULE_BASED','OPEN')
            """,
            (
                candidate.get("store_id"),
                candidate.get("product_id"),
                candidate.get("sale_id"),
                candidate["anomaly_type"],
                candidate["severity"],
                candidate["description"],
                candidate.get("detected_value"),
                candidate.get("expected_value"),
            ),
        )
        inserted += 1
    return inserted
