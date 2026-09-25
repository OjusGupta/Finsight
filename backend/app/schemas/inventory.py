from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InventoryResponse(BaseModel):
    inventory_id: int
    store_id: int
    product_id: int
    quantity: int
    reorder_level: int
    last_updated: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
