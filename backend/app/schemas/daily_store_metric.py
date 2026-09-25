from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class DailyStoreMetricResponse(BaseModel):
    metric_id: int
    store_id: int
    metric_date: date
    total_sales: Decimal
    total_orders: int
    total_returns: Decimal
    total_expenses: Decimal
    net_sales: Decimal
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)