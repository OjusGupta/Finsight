from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductResponse(BaseModel):
    product_id: int
    category_id: int
    product_name: str
    sku: str
    unit_price: Decimal
    cost_price: Decimal
    is_active: bool | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)