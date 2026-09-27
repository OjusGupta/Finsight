from backend.app.services import finance_analytics_service
from backend.app.schemas import finance_analytics as fa_schemas


def build_latest_finance_context(db) -> dict:
    """Build a concise context dict for the latest reconciliation run.
    Returns a dict with selected fields to keep token usage low.
    """
    latest = finance_analytics_service.get_latest_run_summary(db)
    if not latest:
        return {}
    run_id = latest.run_id
    return build_reconciliation_context(db, run_id)


def build_reconciliation_context(db, run_id: int) -> dict:
    """Assemble core finance context for a specific run_id.
    Includes summary, state counts, store states, and blocked documents.
    """
    summary = finance_analytics_service.get_run_summary(db, run_id)
    states = finance_analytics_service.get_state_counts(db, run_id)
    store_states = finance_analytics_service.get_store_states(db, run_id)
    blocked = finance_analytics_service.get_blocked_documents(db, run_id)
    # Minimal fields
    return {
        "run_id": run_id,
        "summary": summary.dict() if summary else None,
        "states": states.dict() if states else None,
        "store_states": store_states.dict() if store_states else None,
        "blocked_documents": blocked.dict() if blocked else None,
    }


def build_blocked_documents_context(db, run_id: int) -> dict:
    blocked = finance_analytics_service.get_blocked_documents(db, run_id)
    return blocked.dict() if blocked else {}


def build_posting_context(db, run_id: int) -> dict:
    counts = finance_analytics_service.get_posting_counts(db, run_id)
    invoices = finance_analytics_service.get_posting_invoices(db, run_id)
    failures = finance_analytics_service.get_posting_failures(db, run_id)
    return {
        "posting_counts": counts.dict() if counts else None,
        "posting_invoices": invoices.dict() if invoices else None,
        "posting_failures": failures.dict() if failures else None,
    }


def build_anomaly_context(db, run_id: int) -> dict:
    anomaly_summary = finance_analytics_service.get_finance_anomaly_summary(db, run_id)
    all_anomalies = finance_analytics_service.get_all_anomaly_types(db)
    return {
        "anomaly_summary": anomaly_summary.dict() if anomaly_summary else None,
        "all_anomaly_types": all_anomalies.dict() if all_anomalies else None,
    }
