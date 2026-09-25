from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductPerformanceResponse(BaseModel):
    performance_id: int
    product_id: int
    metric_date: date
    units_sold: int
    revenue: Decimal
    units_returned: int
    return_amount: Decimal
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)