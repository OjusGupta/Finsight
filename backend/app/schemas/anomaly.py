from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class AnomalyResponse(BaseModel):
    anomaly_id: int
    store_id: int | None = None
    product_id: int | None = None
    sale_id: int | None = None
    anomaly_type: str
    severity: str
    description: str
    detected_value: Decimal | None = None
    expected_value: Decimal | None = None
    detection_method: str
    status: str
    detected_at: datetime | None = None
    resolved_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)