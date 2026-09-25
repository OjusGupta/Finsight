from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.daily_store_metric import DailyStoreMetricResponse
from backend.app.services.daily_store_metric_service import (
    get_all_daily_store_metrics,
)


router = APIRouter(
    prefix="/api/v1/analytics/daily-store",
    tags=["Analytics"],
)


@router.get("/", response_model=List[DailyStoreMetricResponse])
def read_daily_store_metrics(db: Session = Depends(get_db)):
    return get_all_daily_store_metrics(db)