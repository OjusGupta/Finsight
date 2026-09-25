from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StoreResponse(BaseModel):
    store_id: int
    company_id: int
    store_name: str
    city: str | None = None
    state: str | None = None
    address: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
