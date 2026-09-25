from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.inventory import InventoryResponse
from backend.app.services.inventory_service import get_all_inventory


router = APIRouter(
    prefix="/api/v1/inventory",
    tags=["Inventory"],
)


@router.get("/", response_model=List[InventoryResponse])
def read_inventory(db: Session = Depends(get_db)):
    return get_all_inventory(db)