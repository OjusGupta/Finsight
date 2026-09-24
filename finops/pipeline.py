from __future__ import annotations

import csv
import json
import os
from datetime import date
from pathlib import Path
from typing import Any, Mapping, Sequence

from .accounting_client import AccountingClient, UrllibAccountingClient
from .journal import PostingJournal
from .ledger import PostedLedger
from .models import JobCannotRun
from .posting import PostingEngine


REPORT_KEYS = {
    "run_date",
    "lines_read",
    "duplicate_lines_skipped",
    "lines_rejected",
    "lines_valid",
    "invoices_seen",
    "invoices_posted",
    "invoices_skipped_already_posted",
    "invoices_failed",
    "invoices_rejected",
    "invoices_unknown_customer",
    "amount_posted",
    "sales_amount_posted",
    "returns_amount_posted",
    "amount_rejected",
    "rejects",
    "rejected_invoices",
    "failures",
}


def read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_customers(path: str | Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for row in read_csv_rows(path):
        code = row.get("customer_code") or row.get("code") or row.get("customer_id")
        if code:
            normalized = str(code).strip().upper()
            result[normalized] = normalized
    return result


def run_pipeline(
    lines_path: str | Path,
    customers_path: str | Path,
    run_date: date,
    ledger_path: str | Path = "state/posted_ledger.json",
    journal_path: str | Path = "state/posting_journal.json",
    report_path: str | Path | None = None,
    client: AccountingClient | None = None,
) -> dict[str, Any]:
    if client is None:
        endpoint = os.getenv("ACCOUNTING_API_URL")
        if not endpoint:
            raise JobCannotRun("ACCOUNTING_API_URL is required when no client is supplied")
        client = UrllibAccountingClient(endpoint)

    rows = read_csv_rows(lines_path)
    customers = read_customers(customers_path)
    engine = PostingEngine(client, PostedLedger(ledger_path), PostingJournal(journal_path))
    report = engine.run(rows, customers, run_date)
    if set(report) != REPORT_KEYS:
        raise JobCannotRun("report schema identity failed")
    if report_path is not None:
        target = Path(report_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def exit_code(report: Mapping[str, Any]) -> int:
    return 1 if report["invoices_failed"] else 0


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run deterministic finance reconciliation and posting")
    parser.add_argument("--lines", required=True)
    parser.add_argument("--customers", required=True)
    parser.add_argument("--run-date", required=True)
    parser.add_argument("--ledger", default="state/posted_ledger.json")
    parser.add_argument("--journal", default="state/posting_journal.json")
    parser.add_argument("--report")
    args = parser.parse_args(argv)
    try:
        run_date = date.fromisoformat(args.run_date)
        report = run_pipeline(
            args.lines,
            args.customers,
            run_date,
            args.ledger,
            args.journal,
            args.report,
        )
    except Exception as exc:
        print(f"job_failed: {type(exc).__name__}: {exc}")
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return exit_code(report)
