from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class SaleResponse(BaseModel):
    sale_id: int
    store_id: int
    customer_id: int | None = None
    user_id: int | None = None
    invoice_number: str
    sale_date: datetime | None = None
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    status: str

    model_config = ConfigDict(from_attributes=True)
