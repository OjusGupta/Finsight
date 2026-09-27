from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.finance_analytics import (
    AllAnomalyTypesResponse,
    AnomalySummaryResponse,
    BlockedDocumentsResponse,
    LatestRunResponse,
    PostingCountsResponse,
    PostingFailuresResponse,
    PostingInvoicesResponse,
    ReconciledSalesResponse,
    RunSummaryResponse,
    StateCountsResponse,
    StoreStatesResponse,
)
from backend.app.services import finance_analytics_service

router = APIRouter(prefix="/api/v1/finance/analytics", tags=["Finance Analytics"])


def _require_run(result, run_id: int):
    if result is None:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return result


@router.get("/latest/", response_model=LatestRunResponse)
def read_latest(db: Session = Depends(get_db)):
    result = finance_analytics_service.get_latest_run_summary(db)
    if result is None:
        raise HTTPException(status_code=404, detail="No reconciliation runs found")
    return result


@router.get("/run/{run_id}/summary/", response_model=RunSummaryResponse)
def read_run_summary(run_id: int, db: Session = Depends(get_db)):
    return _require_run(finance_analytics_service.get_run_summary(db, run_id), run_id)


@router.get("/run/{run_id}/states/", response_model=StateCountsResponse)
def read_state_counts(run_id: int, db: Session = Depends(get_db)):
    return _require_run(finance_analytics_service.get_state_counts(db, run_id), run_id)


@router.get("/run/{run_id}/stores/", response_model=StoreStatesResponse)
def read_store_states(run_id: int, db: Session = Depends(get_db)):
    return _require_run(finance_analytics_service.get_store_states(db, run_id), run_id)


@router.get("/run/{run_id}/reconciled-sales/", response_model=ReconciledSalesResponse)
def read_reconciled_sales(run_id: int, db: Session = Depends(get_db)):
    return _require_run(finance_analytics_service.get_reconciled_sales(db, run_id), run_id)


@router.get("/run/{run_id}/blocked/", response_model=BlockedDocumentsResponse)
def read_blocked_documents(run_id: int, db: Session = Depends(get_db)):
    return _require_run(finance_analytics_service.get_blocked_documents(db, run_id), run_id)


@router.get("/run/{run_id}/posting-counts/", response_model=PostingCountsResponse)
def read_posting_counts(run_id: int, db: Session = Depends(get_db)):
    return _require_run(finance_analytics_service.get_posting_counts(db, run_id), run_id)


@router.get("/run/{run_id}/posting-invoices/", response_model=PostingInvoicesResponse)
def read_posting_invoices(run_id: int, db: Session = Depends(get_db)):
    return _require_run(finance_analytics_service.get_posting_invoices(db, run_id), run_id)


@router.get("/run/{run_id}/posting-failures/", response_model=PostingFailuresResponse)
def read_posting_failures(run_id: int, db: Session = Depends(get_db)):
    return _require_run(finance_analytics_service.get_posting_failures(db, run_id), run_id)


@router.get("/run/{run_id}/anomalies/", response_model=AnomalySummaryResponse)
def read_finance_anomaly_summary(run_id: int, db: Session = Depends(get_db)):
    return _require_run(
        finance_analytics_service.get_finance_anomaly_summary(db, run_id), run_id
    )


@router.get("/anomaly-types/", response_model=AllAnomalyTypesResponse)
def read_all_anomaly_types(db: Session = Depends(get_db)):
    return finance_analytics_service.get_all_anomaly_types(db)
