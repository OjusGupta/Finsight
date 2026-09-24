from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any, Mapping


@dataclass(frozen=True)
class NormalizedLine:
    invoice_no: str
    line_no: str
    doc_type: str
    transaction_date: date
    customer_code: str | None
    line_total: Decimal
    taxable_value: Decimal | None
    gst_amount: Decimal | None
    raw: Mapping[str, Any]
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LineReject:
    invoice_no: str
    line_no: str
    reason: str
    details: str = ""


@dataclass(frozen=True)
class InvoiceDocument:
    invoice_no: str
    doc_type: str
    customer_code: str | None
    lines: tuple[NormalizedLine, ...]

    @property
    def total(self) -> Decimal:
        return sum((line.line_total for line in self.lines), Decimal("0.00"))

    def as_payload(self) -> dict[str, Any]:
        return {
            "invoice_no": self.invoice_no,
            "doc_type": self.doc_type,
            "customer_code": self.customer_code,
            "lines": [
                {
                    "line_no": line.line_no,
                    "transaction_date": line.transaction_date.isoformat(),
                    "line_total": f"{line.line_total:.2f}",
                    "taxable_value": (
                        f"{line.taxable_value:.2f}"
                        if line.taxable_value is not None
                        else None
                    ),
                    "gst_amount": (
                        f"{line.gst_amount:.2f}"
                        if line.gst_amount is not None
                        else None
                    ),
                }
                for line in self.lines
            ],
            "total": f"{self.total:.2f}",
        }


@dataclass(frozen=True)
class AccountingResponse:
    status_code: int
    document_id: str | None = None
    body: Mapping[str, Any] | None = None


class AccountingTimeout(Exception):
    """Raised when a request may have succeeded but no response was received."""


class JobCannotRun(Exception):
    """Raised when required local processing state cannot be loaded or written."""
