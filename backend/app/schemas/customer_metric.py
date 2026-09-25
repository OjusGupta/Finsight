from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CustomerMetricResponse(BaseModel):
    metric_id: int
    customer_id: int
    metric_date: date
    total_orders: int
    total_spent: Decimal
    total_items_purchased: int
    total_returns: int
    total_refund_amount: Decimal
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)