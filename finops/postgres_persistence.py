from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Mapping, Sequence

from psycopg2.extras import Json

from .models import InvoiceDocument, NormalizedLine


class PostgresPersistence:
    """PostgreSQL-backed run, line, ledger, and posting-attempt state."""

    def __init__(self, connection: Any, run_id: int | None = None):
        self.connection = connection
        self.run_id = run_id

    def create_run(
        self,
        adapter_report: Mapping[str, Any],
        reconciliation_report: Mapping[str, Any],
        source_system: str = "finsight_postgres",
    ) -> int:
        state_counts = reconciliation_report.get("state_counts", {})
        status = "COMPLETED_WITH_BLOCKS" if reconciliation_report.get(
            "invoices_blocked_from_posting", 0
        ) else "COMPLETED"
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO finance_reconciliation_runs (
                source_system, status, lines_read, lines_valid, lines_rejected,
                duplicate_lines_skipped, invoices_processed, invoices_reconciled,
                invoices_blocked, amount_reconciled, amount_blocked, summary_json
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING run_id
            """,
            (
                source_system,
                status,
                reconciliation_report.get("lines_read", 0),
                reconciliation_report.get("structurally_valid_lines", 0),
                reconciliation_report.get("invalid_lines", 0),
                reconciliation_report.get("duplicate_lines_skipped", 0),
                reconciliation_report.get("invoices_processed", 0),
                reconciliation_report.get("invoices_reconciled", 0),
                reconciliation_report.get("invoices_blocked_from_posting", 0),
                Decimal(reconciliation_report.get("amount_reconciled", "0.00")),
                self._blocked_amount(reconciliation_report),
                Json({
                    "adapter": adapter_report,
                    "reconciliation": reconciliation_report,
                    "state_counts": state_counts,
                }),
            ),
        )
        self.run_id = int(cursor.fetchone()[0])
        return self.run_id

    def persist_lines(
        self,
        lines: Sequence[NormalizedLine],
        reconciliation_report: Mapping[str, Any],
    ) -> int:
        if self.run_id is None:
            raise RuntimeError("create_run must be called before persist_lines")
        states = {
            item["invoice_no"]: item
            for item in reconciliation_report.get("invoice_states", [])
        }
        cursor = self.connection.cursor()
        for line in lines:
            state = states.get(line.invoice_no, {})
            metadata = dict(line.metadata)
            cursor.execute(
                """
                INSERT INTO finance_reconciliation_lines (
                    run_id, source_table, source_id, company_id, store_id,
                    customer_id, product_id, sale_id, sale_item_id, return_id,
                    return_item_id, invoice_no, line_no, doc_type,
                    transaction_date, customer_code, line_total, taxable_value,
                    gst_amount, finance_state, rejection_reason,
                    posting_allowed, metadata
                ) VALUES (
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s
                )
                """,
                (
                    self.run_id,
                    metadata.get("source_table", ""),
                    int(metadata.get("source_id")),
                    metadata.get("company_id"),
                    metadata.get("store_id"),
                    metadata.get("customer_id"),
                    metadata.get("product_id"),
                    metadata.get("sale_id"),
                    metadata.get("sale_item_id"),
                    metadata.get("return_id"),
                    metadata.get("return_item_id"),
                    line.invoice_no,
                    line.line_no,
                    line.doc_type,
                    line.transaction_date,
                    line.customer_code,
                    line.line_total,
                    line.taxable_value,
                    line.gst_amount,
                    state.get("state", "REJECTED"),
                    state.get("reason"),
                    bool(state.get("posting_allowed", False)),
                    Json(metadata),
                ),
            )
        return len(lines)

    def finalize_run(self, status: str | None = None, error: str | None = None) -> None:
        if self.run_id is None:
            raise RuntimeError("run_id is not set")
        cursor = self.connection.cursor()
        if status is None:
            status = "COMPLETED"
        cursor.execute(
            """
            UPDATE finance_reconciliation_runs
            SET status=%s, error_message=%s, run_completed_at=CURRENT_TIMESTAMP
            WHERE run_id=%s
            """,
            (status, error, self.run_id),
        )

    def contains(self, invoice_no: str) -> bool:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT 1 FROM accounting_postings
            WHERE idempotency_key=%s
              AND posting_status IN ('POSTED', 'ALREADY_POSTED')
            LIMIT 1
            """,
            (invoice_no,),
        )
        return cursor.fetchone() is not None

    def record(self, invoice_no: str, second: Any, third: Any = None, **result: Any) -> None:
        if isinstance(second, int):
            self._record_attempt(invoice_no, second, result)
        else:
            self._record_final(invoice_no, second, third)

    def _record_attempt(self, invoice_no: str, attempt: int, result: Mapping[str, Any]) -> None:
        if self.run_id is None:
            raise RuntimeError("run_id is not set")
        status_code = result.get("status_code")
        outcome = result.get("result", "failure")
        posting_status = {
            "success": "POSTING",
            "already_posted": "POSTING",
            "timeout": "TIMEOUT",
            "retryable_failure": "RETRYABLE_FAILURE",
            "permanent_failure": "PERMANENT_FAILURE",
        }.get(outcome, "FAILED")
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        entry = dict(result)
        entry["attempt"] = attempt
        doc_type = "sales_return" if invoice_no.startswith("sales_return:") else "sale"
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO accounting_postings (
                run_id, invoice_no, doc_type, idempotency_key,
                reconciliation_state, posting_status, attempt_count,
                last_http_status, last_result, last_error, timeout_observed,
                attempt_history, first_attempt_at, last_attempt_at, updated_at
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (idempotency_key) DO UPDATE SET
                attempt_count=EXCLUDED.attempt_count,
                last_http_status=EXCLUDED.last_http_status,
                last_result=EXCLUDED.last_result,
                last_error=EXCLUDED.last_error,
                timeout_observed=accounting_postings.timeout_observed OR EXCLUDED.timeout_observed,
                attempt_history=accounting_postings.attempt_history || EXCLUDED.attempt_history,
                last_attempt_at=EXCLUDED.last_attempt_at,
                updated_at=EXCLUDED.updated_at,
                posting_status=EXCLUDED.posting_status
            """,
            (
                self.run_id,
                invoice_no,
                doc_type,
                invoice_no,
                "RECONCILED",
                posting_status,
                attempt,
                status_code,
                outcome,
                result.get("error"),
                outcome == "timeout",
                Json([entry]),
                now,
                now,
                now,
            ),
        )

    def _record_final(self, invoice_no: str, document_id: str | None, outcome: str) -> None:
        if self.run_id is None:
            raise RuntimeError("run_id is not set")
        status = "ALREADY_POSTED" if outcome == "already_posted" else "POSTED"
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE accounting_postings
            SET posting_status=%s, external_document_id=%s,
                posted_at=%s, updated_at=%s
            WHERE run_id=%s AND invoice_no=%s
            """,
            (status, document_id, now, now, self.run_id, invoice_no),
        )

    @staticmethod
    def _blocked_amount(report: Mapping[str, Any]) -> Decimal:
        total = Decimal("0.00")
        for item in report.get("invoice_states", []):
            if item.get("state") != "RECONCILED":
                total += abs(Decimal(item.get("amount", "0.00")))
        return total
