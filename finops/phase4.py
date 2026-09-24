from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Sequence

from .accounting_client import AccountingClient
from .erp_adapter import build_finance_lines
from .integration import reconcile_adapter_result
from .mock_accounting import MockAccountingClient
from .models import InvoiceDocument, NormalizedLine
from .postgres_persistence import PostgresPersistence
from .posting import PostingEngine


def connect_writable(env_path: str | Path | None = None):
    from .erp_adapter import _load_env, DEFAULT_ENV_PATH
    import os
    import psycopg2

    _load_env(env_path or DEFAULT_ENV_PATH)
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "finsight"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=5,
    )


def _reconciled_documents(
    lines: Sequence[NormalizedLine],
    reconciliation_report: dict[str, Any],
) -> tuple[InvoiceDocument, ...]:
    allowed = {
        item["invoice_no"]
        for item in reconciliation_report["invoice_states"]
        if item["state"] == "RECONCILED"
    }
    grouped: dict[str, list[NormalizedLine]] = {}
    for line in lines:
        if line.invoice_no in allowed:
            grouped.setdefault(line.invoice_no, []).append(line)
    return tuple(
        InvoiceDocument(
            invoice_no=invoice_no,
            doc_type=group[0].doc_type,
            customer_code=group[0].customer_code,
            lines=tuple(group),
        )
        for invoice_no, group in sorted(grouped.items())
    )


def run_live_phase4(
    env_path: str | Path | None = None,
    client: AccountingClient | None = None,
) -> dict[str, Any]:
    adapter_result = (
        build_finance_lines(env_path=env_path)
        if env_path is not None
        else build_finance_lines()
    )
    integrated = reconcile_adapter_result(adapter_result)
    reconciliation = integrated["reconciliation"]
    documents = _reconciled_documents(adapter_result.lines, reconciliation)
    client = client or MockAccountingClient()

    connection = connect_writable(env_path)
    try:
        persistence = PostgresPersistence(connection)
        run_id = persistence.create_run(adapter_result.report, reconciliation)
        persistence.persist_lines(adapter_result.lines, reconciliation)
        posting = PostingEngine(client, persistence, persistence)
        posting_report = posting.post_documents(documents)
        persistence.finalize_run(
            "COMPLETED_WITH_BLOCKS"
            if reconciliation["invoices_blocked_from_posting"]
            else "COMPLETED"
        )
        connection.commit()
        return {
            "run_id": run_id,
            "adapter": adapter_result.report,
            "reconciliation": reconciliation,
            "posting": posting_report,
            "mock_calls": len(getattr(client, "calls", [])),
        }
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
