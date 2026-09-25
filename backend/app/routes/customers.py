from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.customer import CustomerResponse
from backend.app.services.customer_service import get_all_customers


router = APIRouter(
    prefix="/api/v1/customers",
    tags=["Customers"],
)


@router.get("/", response_model=List[CustomerResponse])
def read_customers(db: Session = Depends(get_db)):
    return get_all_customers(db)
