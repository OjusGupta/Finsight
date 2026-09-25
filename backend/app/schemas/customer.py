from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CustomerResponse(BaseModel):
    customer_id: int
    full_name: str
    email: str | None = None
    phone: str | None = None
    city: str | None = None
    state: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)