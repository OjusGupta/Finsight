from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.sale import SaleResponse
from backend.app.services.sale_service import get_all_sales


router = APIRouter(
    prefix="/api/v1/sales",
    tags=["Sales"],
)


@router.get("/", response_model=List[SaleResponse])
def read_sales(db: Session = Depends(get_db)):
    return get_all_sales(db)
