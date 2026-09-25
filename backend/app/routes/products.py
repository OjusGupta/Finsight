from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.product import ProductResponse
from backend.app.services.product_service import get_all_products


router = APIRouter(
    prefix="/api/v1/products",
    tags=["Products"],
)


@router.get("/", response_model=List[ProductResponse])
def read_products(db: Session = Depends(get_db)):
    return get_all_products(db)