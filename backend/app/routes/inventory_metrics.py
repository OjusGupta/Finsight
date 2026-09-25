from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.inventory_metric import InventoryMetricResponse
from backend.app.services.inventory_metric_service import (
    get_all_inventory_metrics,
)


router = APIRouter(
    prefix="/api/v1/analytics/inventory-metrics",
    tags=["Analytics"],
)


@router.get("/", response_model=List[InventoryMetricResponse])
def read_inventory_metrics(db: Session = Depends(get_db)):
    return get_all_inventory_metrics(db)