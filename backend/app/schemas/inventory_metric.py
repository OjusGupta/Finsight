from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class InventoryMetricResponse(BaseModel):
    metric_id: int
    inventory_id: int
    metric_date: date
    opening_quantity: int
    closing_quantity: int
    units_sold: int
    units_received: int
    units_returned: int
    stock_value: Decimal
    reorder_level: int
    stock_status: str
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)