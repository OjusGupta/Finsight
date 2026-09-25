from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.store import StoreResponse
from backend.app.services.store_service import get_all_stores


router = APIRouter(
    prefix="/api/v1/stores",
    tags=["Stores"],
)


@router.get("/", response_model=List[StoreResponse])
def read_stores(db: Session = Depends(get_db)):
    return get_all_stores(db)