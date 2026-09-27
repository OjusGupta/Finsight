from langchain_core.tools import tool
from sqlalchemy.orm import Session
from backend.app.services import finance_analytics_service

def get_finance_tools(db: Session):
    
    @tool
    def get_latest_finance_summary():
        """Get the summary of the latest finance reconciliation run."""
        latest_run = finance_analytics_service.get_latest_run_summary(db)
        if not latest_run:
            return {"error": "No finance runs found."}
        
        return finance_analytics_service.get_run_summary(db, latest_run.run_id).model_dump(mode="json")
    
    @tool
    def get_blocked_finance_documents():
        """Get blocked finance documents from the latest reconciliation run."""
        latest_run = finance_analytics_service.get_latest_run_summary(db)
        if not latest_run:
            return {"error": "No finance runs found."}
            
        res = finance_analytics_service.get_blocked_documents(db, latest_run.run_id)
        return res.model_dump(mode="json") if res else {"error": "No blocked documents found."}
        
    @tool
    def get_finance_states():
        """Get state counts from the latest finance reconciliation run."""
        latest_run = finance_analytics_service.get_latest_run_summary(db)
        if not latest_run:
            return {"error": "No finance runs found."}
            
        res = finance_analytics_service.get_state_counts(db, latest_run.run_id)
        return res.model_dump(mode="json") if res else {"error": "No state counts found."}

    @tool
    def get_finance_posting_status():
        """Get posting status counts and failures from the latest finance run."""
        latest_run = finance_analytics_service.get_latest_run_summary(db)
        if not latest_run:
            return {"error": "No finance runs found."}
            
        counts = finance_analytics_service.get_posting_counts(db, latest_run.run_id)
        failures = finance_analytics_service.get_posting_failures(db, latest_run.run_id)
        return {
            "counts": counts.model_dump(mode="json") if counts else None,
            "failures": failures.model_dump(mode="json") if failures else None
        }

    @tool
    def get_finance_anomalies():
        """Get finance anomaly summary from the latest finance run."""
        latest_run = finance_analytics_service.get_latest_run_summary(db)
        if not latest_run:
            return {"error": "No finance runs found."}
            
        res = finance_analytics_service.get_finance_anomaly_summary(db, latest_run.run_id)
        return res.model_dump(mode="json") if res else {"error": "No anomalies found."}

    return [
        get_latest_finance_summary,
        get_blocked_finance_documents,
        get_finance_states,
        get_finance_posting_status,
        get_finance_anomalies,
    ]
