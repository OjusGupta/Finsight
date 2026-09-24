from __future__ import annotations

from datetime import date
from typing import Any, Mapping

from .models import LineReject, NormalizedLine
from .money import parse_money
from .parsing import parse_business_date


_MISSING = object()


def _value(row: Mapping[str, Any], *names: str, default: Any = _MISSING) -> Any:
    for name in names:
        if name in row and row[name] is not None and str(row[name]).strip() != "":
            return row[name]
    if default is not _MISSING:
        return default
    raise ValueError("missing_field")


def validate_line(row: Mapping[str, Any], run_date: date) -> NormalizedLine | LineReject:
    invoice_no = str(row.get("invoice_no", "")).strip()
    line_no = str(row.get("line_no", "")).strip()

    try:
        if not invoice_no or not line_no:
            raise ValueError("missing_field")

        doc_type = str(_value(row, "doc_type")).strip().lower()
        if doc_type not in {"sale", "sales_return"}:
            raise ValueError("invalid_doc_type")

        transaction_date = parse_business_date(
            _value(row, "transaction_date", "date", "sale_date")
        )
        if transaction_date > run_date:
            raise ValueError("future_date")

        line_total = parse_money(_value(row, "line_total"))
        taxable_value = parse_money(_value(row, "taxable_value"))
        gst_amount = parse_money(_value(row, "gst_amount"))

        if doc_type == "sale" and line_total <= 0:
            raise ValueError("sign_mismatch")
        if doc_type == "sales_return" and line_total >= 0:
            raise ValueError("sign_mismatch")

        return NormalizedLine(
            invoice_no=invoice_no,
            line_no=line_no,
            doc_type=doc_type,
            transaction_date=transaction_date,
            customer_code=str(row.get("customer_code", "")).strip(),
            line_total=line_total,
            taxable_value=taxable_value,
            gst_amount=gst_amount,
            raw=dict(row),
        )
    except ValueError as exc:
        return LineReject(invoice_no, line_no, str(exc))
