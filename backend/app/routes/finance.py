from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.accounting_posting import AccountingPostingResponse
from backend.app.schemas.anomaly import AnomalyResponse
from backend.app.schemas.finance_reconciliation_line import FinanceReconciliationLineResponse
from backend.app.schemas.finance_reconciliation_run import FinanceReconciliationRunResponse
from backend.app.services import finance_service

router = APIRouter(prefix="/api/v1/finance", tags=["Finance"])


@router.get("/runs/", response_model=List[FinanceReconciliationRunResponse])
def read_runs(db: Session = Depends(get_db)):
    return finance_service.get_all_runs(db)


@router.get("/runs/latest/", response_model=FinanceReconciliationRunResponse)
def read_latest_run(db: Session = Depends(get_db)):
    run = finance_service.get_latest_run(db)
    if run is None:
        raise HTTPException(status_code=404, detail="No reconciliation runs found")
    return run


@router.get("/runs/{run_id}/", response_model=FinanceReconciliationRunResponse)
def read_run(run_id: int, db: Session = Depends(get_db)):
    run = finance_service.get_run_by_id(db, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return run


@router.get("/runs/{run_id}/lines/", response_model=List[FinanceReconciliationLineResponse])
def read_lines_for_run(run_id: int, db: Session = Depends(get_db)):
    return finance_service.get_lines_by_run(db, run_id)


@router.get("/runs/{run_id}/postings/", response_model=List[AccountingPostingResponse])
def read_postings_for_run(run_id: int, db: Session = Depends(get_db)):
    return finance_service.get_postings_by_run(db, run_id)


@router.get("/lines/", response_model=List[FinanceReconciliationLineResponse])
def read_all_lines(db: Session = Depends(get_db)):
    return finance_service.get_all_lines(db)


@router.get("/postings/", response_model=List[AccountingPostingResponse])
def read_all_postings(db: Session = Depends(get_db)):
    return finance_service.get_all_postings(db)


@router.get("/anomalies/", response_model=List[AnomalyResponse])
def read_finance_anomalies(db: Session = Depends(get_db)):
    return finance_service.get_finance_anomalies(db)
