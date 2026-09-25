from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.anomaly import AnomalyResponse
from backend.app.services.anomaly_service import get_all_anomalies


router = APIRouter(
    prefix="/api/v1/anomalies",
    tags=["Anomalies"],
)


@router.get("/", response_model=List[AnomalyResponse])
def read_anomalies(db: Session = Depends(get_db)):
    return get_all_anomalies(db)