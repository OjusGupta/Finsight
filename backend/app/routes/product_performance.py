from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.product_performance import ProductPerformanceResponse
from backend.app.services.product_performance_service import (
    get_all_product_performance,
)


router = APIRouter(
    prefix="/api/v1/analytics/product-performance",
    tags=["Analytics"],
)


@router.get("/", response_model=List[ProductPerformanceResponse])
def read_product_performance(db: Session = Depends(get_db)):
    return get_all_product_performance(db)