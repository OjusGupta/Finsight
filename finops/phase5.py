from __future__ import annotations

from pathlib import Path
from typing import Any

from .finance_analytics import (
    FinanceAnalytics,
    build_finance_anomaly_candidates,
    persist_finance_anomalies,
)
from .phase4 import connect_writable


def run_phase5(
    env_path: str | Path | None = None,
    persist_anomalies: bool = True,
) -> dict[str, Any]:
    connection = connect_writable(env_path)
    try:
        analytics = FinanceAnalytics(connection)
        run_id = analytics.latest_run_id()
        report = analytics.report(run_id)
        line_rows = analytics.finance_line_rows(run_id)
        posting_rows = analytics.posting_rows(run_id)
        candidates = build_finance_anomaly_candidates(line_rows, posting_rows)
        inserted = 0
        if persist_anomalies:
            inserted = persist_finance_anomalies(connection, candidates)
            connection.commit()
        return {
            "run_id": run_id,
            "analytics": report,
            "anomaly_candidates": len(candidates),
            "anomalies_inserted": inserted,
        }
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
