from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Iterable, Mapping, Sequence

from .models import InvoiceDocument, LineReject, NormalizedLine
from .money import format_money


@dataclass(frozen=True)
class InvoiceValidation:
    document: InvoiceDocument | None
    reason: str | None
    amount: Decimal


def normalize_customer_code(value: object) -> str:
    return str(value or "").strip().upper()


def resolve_customer(customer_code: str, customers: Mapping[str, str]) -> tuple[str, bool]:
    normalized = normalize_customer_code(customer_code)
    if normalized and normalized in customers:
        return customers[normalized], False
    return "UNKNOWN", True


def group_lines(lines: Iterable[NormalizedLine]) -> dict[str, list[NormalizedLine]]:
    grouped: dict[str, list[NormalizedLine]] = defaultdict(list)
    for line in lines:
        grouped[line.invoice_no].append(line)
    return dict(grouped)


def reconcile_invoice(
    invoice_no: str,
    lines: list[NormalizedLine],
    customers: Mapping[str, str],
) -> tuple[InvoiceValidation, bool]:
    customer_code, unknown = resolve_customer(lines[0].customer_code if lines else "", customers)
    amount = sum((line.line_total for line in lines), Decimal("0.00"))
    if any(
        line.taxable_value is None or line.gst_amount is None
        for line in lines
    ):
        return InvoiceValidation(None, "missing_financial_fields", amount), unknown
    comparison = sum(
        (line.taxable_value + line.gst_amount for line in lines), Decimal("0.00")
    )
    tolerance = Decimal("0.05") * len(lines)
    if abs(amount - comparison) > tolerance:
        return InvoiceValidation(None, "total_mismatch", amount), unknown

    doc_type = lines[0].doc_type
    if any(line.doc_type != doc_type for line in lines):
        return InvoiceValidation(None, "incomplete_invoice", amount), unknown

    return (
        InvoiceValidation(
            InvoiceDocument(invoice_no, doc_type, customer_code, tuple(lines)),
            None,
            amount,
        ),
        unknown,
    )


def invoice_amounts(lines: Iterable[NormalizedLine]) -> tuple[Decimal, Decimal, Decimal]:
    total = sum((line.line_total for line in lines), Decimal("0.00"))
    sales = sum((line.line_total for line in lines if line.doc_type == "sale"), Decimal("0.00"))
    returns = sum(
        (line.line_total for line in lines if line.doc_type == "sales_return"),
        Decimal("0.00"),
    )
    return total, sales, returns


def _normalized_line_error(line: NormalizedLine) -> str | None:
    if not line.invoice_no or not line.line_no:
        return "missing_field"
    if line.doc_type not in {"sale", "sales_return"}:
        return "invalid_doc_type"
    if line.doc_type == "sale" and line.line_total <= 0:
        return "sign_mismatch"
    if line.doc_type == "sales_return" and line.line_total >= 0:
        return "sign_mismatch"
    return None


def reconcile_normalized_lines(
    lines: Sequence[NormalizedLine],
) -> dict[str, Any]:
    """Reconcile adapter output without posting or creating execution state."""
    grouped: dict[str, list[NormalizedLine]] = defaultdict(list)
    identity_groups: dict[tuple[str, str], list[NormalizedLine]] = defaultdict(list)
    for line in lines:
        grouped[line.invoice_no].append(line)
        identity_groups[(line.invoice_no, line.line_no)].append(line)

    duplicate_lines_skipped = 0
    conflicting_invoice_numbers: set[str] = set()
    deduplicated: list[NormalizedLine] = []
    for identity, candidates in identity_groups.items():
        if len(candidates) == 1:
            deduplicated.append(candidates[0])
        elif all(candidate == candidates[0] for candidate in candidates[1:]):
            deduplicated.append(candidates[0])
            duplicate_lines_skipped += len(candidates) - 1
        else:
            conflicting_invoice_numbers.add(identity[0])

    unique_grouped: dict[str, list[NormalizedLine]] = defaultdict(list)
    for line in deduplicated:
        unique_grouped[line.invoice_no].append(line)

    invalid_lines = 0
    structurally_valid_lines = 0
    invalid_by_invoice: dict[str, list[dict[str, str]]] = defaultdict(list)
    for line in deduplicated:
        error = _normalized_line_error(line)
        if error:
            invalid_lines += 1
            invalid_by_invoice[line.invoice_no].append(
                {"line_no": line.line_no, "reason": error}
            )
        else:
            structurally_valid_lines += 1

    missing_financial_fields = {
        "customer_code": sum(line.customer_code is None for line in lines),
        "taxable_value": sum(line.taxable_value is None for line in lines),
        "gst_amount": sum(line.gst_amount is None for line in lines),
    }
    invoice_states: list[dict[str, Any]] = []
    amount_reconciled = Decimal("0.00")
    sales_amount_reconciled = Decimal("0.00")
    returns_amount_reconciled = Decimal("0.00")
    state_counts: dict[str, int] = defaultdict(int)

    for invoice_no in sorted({line.invoice_no for line in lines}):
        invoice_lines = unique_grouped.get(invoice_no, [])
        amount = sum((line.line_total for line in invoice_lines), Decimal("0.00"))
        state: str
        reason: str | None = None
        details: dict[str, Any] = {}

        if invoice_no in conflicting_invoice_numbers:
            state = "CONFLICTING_DUPLICATE"
            reason = "conflicting_duplicate"
        elif invalid_by_invoice.get(invoice_no):
            state = "INCOMPLETE_INVOICE"
            reason = "incomplete_invoice"
            details["invalid_lines"] = invalid_by_invoice[invoice_no]
        elif any(
            line.taxable_value is None or line.gst_amount is None
            for line in invoice_lines
        ):
            state = "FINANCE_FIELDS_INCOMPLETE"
            reason = "missing taxable_value/gst_amount"
            details["posting_allowed"] = False
        else:
            validation, _ = reconcile_invoice(invoice_no, invoice_lines, {})
            if validation.reason == "total_mismatch":
                state = "TOTAL_MISMATCH"
                reason = validation.reason
            elif validation.reason:
                state = "INCOMPLETE_INVOICE"
                reason = validation.reason
            else:
                state = "RECONCILED"
                amount_reconciled += amount
                _, sales_amount, returns_amount = invoice_amounts(invoice_lines)
                sales_amount_reconciled += sales_amount
                returns_amount_reconciled += returns_amount
                details["posting_allowed"] = True

        state_counts[state] += 1
        invoice_states.append(
            {
                "invoice_no": invoice_no,
                "state": state,
                "reason": reason,
                "line_count": len(invoice_lines),
                "amount": format_money(amount),
                **details,
            }
        )

    blocked_states = {
        state
        for state in state_counts
        if state != "RECONCILED"
    }
    return {
        "lines_read": len(lines),
        "duplicate_lines_skipped": duplicate_lines_skipped,
        "conflicting_duplicate_invoices": len(conflicting_invoice_numbers),
        "structurally_valid_lines": structurally_valid_lines,
        "invalid_lines": invalid_lines,
        "invoices_processed": len(invoice_states),
        "invoices_reconciled": state_counts.get("RECONCILED", 0),
        "invoices_eligible_for_complete_reconciliation": state_counts.get("RECONCILED", 0),
        "invoices_blocked_from_posting": sum(
            count for state, count in state_counts.items() if state in blocked_states
        ),
        "state_counts": dict(sorted(state_counts.items())),
        "missing_financial_fields": missing_financial_fields,
        "amount_reconciled": format_money(amount_reconciled),
        "sales_amount_reconciled": format_money(sales_amount_reconciled),
        "returns_amount_reconciled": format_money(returns_amount_reconciled),
        "invoice_states": invoice_states,
    }
