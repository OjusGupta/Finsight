from __future__ import annotations

import os
from datetime import date, datetime
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping, Sequence

import psycopg2
import psycopg2.extras

from .models import NormalizedLine


DEFAULT_ENV_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "FinSight_synthetic_ERP_dataset_v1"
    / "reference"
    / ".env"
)


@dataclass(frozen=True)
class AdapterResult:
    lines: tuple[NormalizedLine, ...]
    report: dict[str, Any]


SALE_COUNT_SQL = """
SELECT
    COUNT(DISTINCT s.sale_id) AS sales_read,
    COUNT(si.sale_item_id) AS sale_items_read
FROM sales s
LEFT JOIN sale_items si ON si.sale_id = s.sale_id
WHERE s.status = 'COMPLETED'
"""

SALE_LINES_SQL = """
SELECT
    st.company_id,
    s.store_id,
    s.customer_id,
    s.sale_id,
    si.sale_item_id,
    si.product_id,
    s.invoice_number,
    s.sale_date,
    si.quantity,
    si.unit_price,
    si.discount_amount,
    si.tax_amount,
    si.line_total,
    s.status AS sale_status
FROM sales s
JOIN sale_items si ON si.sale_id = s.sale_id
JOIN stores st ON st.store_id = s.store_id
WHERE s.status = 'COMPLETED'
ORDER BY s.sale_id, si.sale_item_id
"""

RETURN_COUNT_SQL = """
SELECT
    COUNT(DISTINCT r.return_id) AS returns_read,
    COUNT(ri.return_item_id) AS return_items_read
FROM returns r
LEFT JOIN return_items ri ON ri.return_id = r.return_id
 WHERE r.status IN ('APPROVED', 'COMPLETED')
"""

RETURN_LINES_SQL = """
SELECT
    st.company_id,
    s.store_id,
    r.customer_id,
    r.sale_id,
    r.return_id,
    ri.return_item_id,
    ri.sale_item_id,
    si.sale_id AS matched_sale_id,
    si.product_id,
    r.return_date,
    ri.refund_amount,
    r.status AS return_status
FROM returns r
JOIN sales s ON s.sale_id = r.sale_id
JOIN stores st ON st.store_id = s.store_id
JOIN return_items ri ON ri.return_id = r.return_id
LEFT JOIN sale_items si ON si.sale_item_id = ri.sale_item_id
WHERE r.status IN ('APPROVED', 'COMPLETED')
ORDER BY r.return_id, ri.return_item_id
"""


def _load_env(path: str | Path = DEFAULT_ENV_PATH) -> None:
    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip().strip('"').strip("'")


def connect_read_only(env_path: str | Path = DEFAULT_ENV_PATH):
    _load_env(env_path)
    connection = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "finsight"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=5,
    )
    connection.set_session(readonly=True, autocommit=True)
    return connection


def _decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _date_value(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def _missing_fields(metadata: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(metadata["missing_financial_fields"])


def _base_metadata(
    *,
    company_id: Any,
    store_id: Any,
    customer_id: Any,
    sale_id: Any,
    sale_item_id: Any,
    return_id: Any,
    return_item_id: Any,
    product_id: Any,
    source_table: str,
    source_id: Any,
    missing_financial_fields: Sequence[str],
    tax_status: str,
) -> dict[str, Any]:
    return {
        "company_id": company_id,
        "store_id": store_id,
        "customer_id": customer_id,
        "sale_id": sale_id,
        "sale_item_id": sale_item_id,
        "return_id": return_id,
        "return_item_id": return_item_id,
        "product_id": product_id,
        "source_table": source_table,
        "source_id": source_id,
        "missing_financial_fields": tuple(missing_financial_fields),
        "customer_code_status": "not_available_in_live_schema",
        "tax_status": tax_status,
    }


def _empty_report(counts: Mapping[str, int]) -> dict[str, Any]:
    return {
        "sales_read": counts.get("sales_read", 0),
        "sale_items_read": counts.get("sale_items_read", 0),
        "normalized_sale_lines": 0,
        "returns_read": counts.get("returns_read", 0),
        "return_items_read": counts.get("return_items_read", 0),
        "normalized_return_lines": 0,
        "skipped_records": [],
        "rejected_records": [],
        "missing_references": [],
        "customer_id_coverage": {
            "lines_total": 0,
            "present": 0,
            "missing": 0,
        },
        "missing_financial_fields": {
            "customer_code": 0,
            "taxable_value": 0,
            "gst_amount": 0,
        },
        "ambiguous_mappings": [],
    }


def build_finance_lines_from_rows(
    sale_rows: Sequence[Mapping[str, Any]],
    return_rows: Sequence[Mapping[str, Any]],
    counts: Mapping[str, int] | None = None,
) -> AdapterResult:
    report = _empty_report(
        counts
        or {
            "sales_read": len({row.get("sale_id") for row in sale_rows}),
            "sale_items_read": len(sale_rows),
            "returns_read": len({row.get("return_id") for row in return_rows}),
            "return_items_read": len(return_rows),
        }
    )
    lines: list[NormalizedLine] = []

    for row in sale_rows:
        customer_id = row.get("customer_id")
        metadata = _base_metadata(
            company_id=row.get("company_id"),
            store_id=row.get("store_id"),
            customer_id=customer_id,
            sale_id=row.get("sale_id"),
            sale_item_id=row.get("sale_item_id"),
            return_id=None,
            return_item_id=None,
            product_id=row.get("product_id"),
            source_table="sale_items",
            source_id=row.get("sale_item_id"),
            missing_financial_fields=("customer_code",),
            tax_status="source_tax_restored_as_tax_amount",
        )
        taxable_value = (
            _decimal(row["unit_price"]) * int(row["quantity"])
            - _decimal(row["discount_amount"])
        )
        lines.append(
            NormalizedLine(
                invoice_no=str(row["invoice_number"]),
                line_no=str(row["sale_item_id"]),
                doc_type="sale",
                transaction_date=_date_value(row["sale_date"]),
                customer_code=None,
                line_total=_decimal(row["line_total"]),
                taxable_value=taxable_value,
                gst_amount=_decimal(row["tax_amount"]),
                raw=dict(row),
                metadata=metadata,
            )
        )

    for row in return_rows:
        return_item_id = row.get("return_item_id")
        sale_item_id = row.get("sale_item_id")
        matched_sale_id = row.get("matched_sale_id")
        return_sale_id = row.get("sale_id")
        if not sale_item_id or not row.get("product_id"):
            report["missing_references"].append(
                {
                    "source_table": "return_items",
                    "source_id": return_item_id,
                    "reason": "missing_sale_item_reference",
                }
            )
            report["rejected_records"].append(
                {
                    "source_table": "return_items",
                    "source_id": return_item_id,
                    "reason": "missing_sale_item_reference",
                }
            )
            continue
        if matched_sale_id != return_sale_id:
            report["rejected_records"].append(
                {
                    "source_table": "return_items",
                    "source_id": return_item_id,
                    "reason": "return_sale_item_mismatch",
                }
            )
            continue

        metadata = _base_metadata(
            company_id=row.get("company_id"),
            store_id=row.get("store_id"),
            customer_id=row.get("customer_id"),
            sale_id=return_sale_id,
            sale_item_id=sale_item_id,
            return_id=row.get("return_id"),
            return_item_id=return_item_id,
            product_id=row.get("product_id"),
            source_table="return_items",
            source_id=return_item_id,
            missing_financial_fields=(
                "customer_code",
                "taxable_value",
                "gst_amount",
            ),
            tax_status="return_tax_not_available",
        )
        lines.append(
            NormalizedLine(
                invoice_no=f"sales_return:{row['return_id']}",
                line_no=str(return_item_id),
                doc_type="sales_return",
                transaction_date=_date_value(row["return_date"]),
                customer_code=None,
                line_total=-_decimal(row["refund_amount"]),
                taxable_value=None,
                gst_amount=None,
                raw=dict(row),
                metadata=metadata,
            )
        )

    report["normalized_sale_lines"] = sum(line.doc_type == "sale" for line in lines)
    report["normalized_return_lines"] = sum(
        line.doc_type == "sales_return" for line in lines
    )
    report["customer_id_coverage"]["lines_total"] = len(lines)
    report["customer_id_coverage"]["present"] = sum(
        line.metadata.get("customer_id") is not None for line in lines
    )
    report["customer_id_coverage"]["missing"] = (
        report["customer_id_coverage"]["lines_total"]
        - report["customer_id_coverage"]["present"]
    )
    for line in lines:
        for field_name in _missing_fields(line.metadata):
            report["missing_financial_fields"][field_name] += 1

    return AdapterResult(tuple(lines), report)


def _fetch_rows(cursor: Any, query: str) -> list[dict[str, Any]]:
    cursor.execute(query)
    return [dict(row) for row in cursor.fetchall()]


def build_finance_lines(
    connection: Any | None = None,
    env_path: str | Path = DEFAULT_ENV_PATH,
) -> AdapterResult:
    owns_connection = connection is None
    connection = connection or connect_read_only(env_path)
    try:
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(SALE_COUNT_SQL)
        sale_counts = dict(cursor.fetchone())
        cursor.execute(RETURN_COUNT_SQL)
        return_counts = dict(cursor.fetchone())
        sale_rows = _fetch_rows(cursor, SALE_LINES_SQL)
        return_rows = _fetch_rows(cursor, RETURN_LINES_SQL)
        return build_finance_lines_from_rows(
            sale_rows,
            return_rows,
            {
                "sales_read": int(sale_counts["sales_read"]),
                "sale_items_read": int(sale_counts["sale_items_read"]),
                "returns_read": int(return_counts["returns_read"]),
                "return_items_read": int(return_counts["return_items_read"]),
            },
        )
    finally:
        if owns_connection:
            connection.close()
