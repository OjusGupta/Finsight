from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict


class FinanceReconciliationLineResponse(BaseModel):
    finance_line_id: int
    run_id: int
    source_table: str
    source_id: int
    company_id: int | None = None
    store_id: int | None = None
    customer_id: int | None = None
    product_id: int | None = None
    sale_id: int | None = None
    sale_item_id: int | None = None
    return_id: int | None = None
    return_item_id: int | None = None
    invoice_no: str
    line_no: str
    doc_type: str
    transaction_date: date
    customer_code: str | None = None
    line_total: Decimal
    taxable_value: Decimal | None = None
    gst_amount: Decimal | None = None
    finance_state: str
    rejection_reason: str | None = None
    posting_allowed: bool
    metadata_json: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
