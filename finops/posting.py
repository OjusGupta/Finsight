from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Mapping, Sequence

from .accounting_client import AccountingClient
from .deduplication import deduplicate_lines
from .journal import PostingJournal
from .ledger import PostedLedger
from .models import AccountingResponse, AccountingTimeout, JobCannotRun, LineReject, NormalizedLine
from .money import format_money
from .reconciliation import group_lines, invoice_amounts, reconcile_invoice
from .validation import validate_line


class PostingEngine:
    def __init__(
        self,
        client: AccountingClient,
        ledger: PostedLedger,
        journal: PostingJournal,
        max_attempts: int = 3,
    ):
        if max_attempts < 1:
            raise ValueError("max_attempts must be positive")
        self.client = client
        self.ledger = ledger
        self.journal = journal
        self.max_attempts = max_attempts

    def run(
        self,
        rows: Sequence[Mapping[str, Any]],
        customers: Mapping[str, str],
        run_date: date,
    ) -> dict[str, Any]:
        deduped = deduplicate_lines(list(rows))
        all_invoice_numbers = {
            str(row.get("invoice_no", "")).strip() for row in rows
        }
        line_rejects = list(deduped.rejects)
        normalized: list[NormalizedLine] = []
        invalid_invoices: set[str] = set()
        for row in deduped.rows:
            result = validate_line(row, run_date)
            if isinstance(result, LineReject):
                line_rejects.append(result)
                invalid_invoices.add(result.invoice_no)
            else:
                normalized.append(result)

        grouped = group_lines(normalized)
        report = self._empty_report(run_date)
        report["lines_read"] = len(rows)
        report["duplicate_lines_skipped"] = deduped.duplicate_lines_skipped
        report["lines_rejected"] = len(line_rejects)
        report["lines_valid"] = len(normalized)
        report["invoices_seen"] = len(all_invoice_numbers)
        report["rejects"] = [self._reject_dict(item) for item in line_rejects]

        for invoice_no in sorted(all_invoice_numbers):
            if invoice_no in deduped.conflicting_invoices:
                self._reject_invoice(report, invoice_no, "conflicting_duplicate", Decimal("0.00"))
                continue
            lines = grouped.get(invoice_no, [])
            if invoice_no in invalid_invoices or not lines:
                amount = sum((line.line_total for line in lines), Decimal("0.00"))
                self._reject_invoice(report, invoice_no, "incomplete_invoice", amount)
                continue

            validation, unknown_customer = reconcile_invoice(invoice_no, lines, customers)
            if unknown_customer:
                report["invoices_unknown_customer"] += 1
            if validation.reason:
                self._reject_invoice(report, invoice_no, validation.reason, validation.amount)
                continue
            if validation.document is None:
                self._reject_invoice(report, invoice_no, "incomplete_invoice", validation.amount)
                continue
            self._post_invoice(report, validation.document)

        report["amount_posted"] = format_money(Decimal(report["_amount_posted"]))
        report["sales_amount_posted"] = format_money(Decimal(report["_sales_amount_posted"]))
        report["returns_amount_posted"] = format_money(Decimal(report["_returns_amount_posted"]))
        report["amount_rejected"] = format_money(Decimal(report["_amount_rejected"]))
        report.pop("_amount_posted")
        report.pop("_sales_amount_posted")
        report.pop("_returns_amount_posted")
        report.pop("_amount_rejected")
        self._validate_identities(report)
        return report

    @staticmethod
    def _empty_report(run_date: date) -> dict[str, Any]:
        return {
            "run_date": run_date.isoformat(),
            "lines_read": 0,
            "duplicate_lines_skipped": 0,
            "lines_rejected": 0,
            "lines_valid": 0,
            "invoices_seen": 0,
            "invoices_posted": 0,
            "invoices_skipped_already_posted": 0,
            "invoices_failed": 0,
            "invoices_rejected": 0,
            "invoices_unknown_customer": 0,
            "amount_posted": "0.00",
            "sales_amount_posted": "0.00",
            "returns_amount_posted": "0.00",
            "amount_rejected": "0.00",
            "rejects": [],
            "rejected_invoices": [],
            "failures": [],
            "_amount_posted": Decimal("0.00"),
            "_sales_amount_posted": Decimal("0.00"),
            "_returns_amount_posted": Decimal("0.00"),
            "_amount_rejected": Decimal("0.00"),
        }

    @staticmethod
    def _reject_dict(reject: LineReject) -> dict[str, str]:
        result = {
            "invoice_no": reject.invoice_no,
            "line_no": reject.line_no,
            "reason": reject.reason,
        }
        if reject.details:
            result["details"] = reject.details
        return result

    @staticmethod
    def _reject_invoice(report: dict[str, Any], invoice_no: str, reason: str, amount: Decimal) -> None:
        report["invoices_rejected"] += 1
        report["amount_rejected"] = format_money(
            Decimal(report["_amount_rejected"]) + amount
        )
        report["_amount_rejected"] = Decimal(report["_amount_rejected"]) + amount
        report["rejected_invoices"].append(
            {"invoice_no": invoice_no, "reason": reason}
        )

    def _post_invoice(self, report: dict[str, Any], document: Any) -> None:
        if self.ledger.contains(document.invoice_no):
            report["invoices_skipped_already_posted"] += 1
            return

        for attempt in range(1, self.max_attempts + 1):
            try:
                response = self.client.post(document.as_payload(), document.invoice_no)
            except AccountingTimeout:
                self.journal.record(
                    document.invoice_no,
                    attempt,
                    result="timeout",
                    status_code=None,
                    outcome="retry" if attempt < self.max_attempts else "failure",
                )
                if attempt == self.max_attempts:
                    self._failed(report, document.invoice_no, "invoice_failed", attempt)
                continue
            except Exception as exc:
                self.journal.record(
                    document.invoice_no,
                    attempt,
                    result="exception",
                    status_code=None,
                    outcome="failure",
                    error=type(exc).__name__,
                )
                self._failed(report, document.invoice_no, "invoice_failed", attempt)
                return

            outcome = self._response_outcome(response)
            retryable = response.status_code >= 500
            self.journal.record(
                document.invoice_no,
                attempt,
                result=outcome,
                status_code=response.status_code,
                outcome="retry" if retryable and attempt < self.max_attempts else outcome,
            )
            if response.status_code in (201, 409):
                self.ledger.record(document.invoice_no, response.document_id, outcome)
                report["invoices_posted"] += 1
                total, sales, returns = invoice_amounts(document.lines)
                report["_amount_posted"] += total
                report["_sales_amount_posted"] += sales
                report["_returns_amount_posted"] += returns
                return
            if response.status_code == 422 or not retryable or attempt == self.max_attempts:
                self._failed(report, document.invoice_no, "invoice_failed", attempt, response.status_code)
                return

    @staticmethod
    def _response_outcome(response: AccountingResponse) -> str:
        return {
            201: "success",
            409: "already_posted",
            422: "permanent_failure",
        }.get(response.status_code, "retryable_failure" if response.status_code >= 500 else "failure")

    @staticmethod
    def _failed(
        report: dict[str, Any],
        invoice_no: str,
        reason: str,
        attempts: int,
        status_code: int | None = None,
    ) -> None:
        report["invoices_failed"] += 1
        failure: dict[str, Any] = {
            "invoice_no": invoice_no,
            "reason": reason,
            "attempts": attempts,
        }
        if status_code is not None:
            failure["status_code"] = status_code
        report["failures"].append(failure)

    @staticmethod
    def _validate_identities(report: Mapping[str, Any]) -> None:
        if report["lines_read"] != report["duplicate_lines_skipped"] + report["lines_valid"] + report["lines_rejected"]:
            raise JobCannotRun("line reconciliation identity failed")
        if report["invoices_seen"] != report["invoices_posted"] + report["invoices_skipped_already_posted"] + report["invoices_failed"] + report["invoices_rejected"]:
            raise JobCannotRun("invoice reconciliation identity failed")
