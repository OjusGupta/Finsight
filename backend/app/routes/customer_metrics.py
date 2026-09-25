from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.customer_metric import CustomerMetricResponse
from backend.app.services.customer_metric_service import (
    get_all_customer_metrics,
)


router = APIRouter(
    prefix="/api/v1/analytics/customer-metrics",
    tags=["Analytics"],
)


@router.get("/", response_model=List[CustomerMetricResponse])
def read_customer_metrics(db: Session = Depends(get_db)):
    return get_all_customer_metrics(db)