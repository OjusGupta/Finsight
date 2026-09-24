# Phase 5 — Finance Analytics and Anomaly Integration

## Scope

Phase 5 connects the Phase 4 finance persistence tables to the existing FinSight anomaly system and produces deterministic finance analytics. It does not implement FastAPI, Streamlit, LangGraph, RAG, or AI agents.

No source sales, returns, or ERP data is modified.

## Entry Point

```text
from finops.phase5 import run_phase5

result = run_phase5()
```

`run_phase5` reads the latest reconciliation run from PostgreSQL, builds the analytics report, generates anomaly candidates from blocked lines and posting failures, persists new anomalies idempotently, and returns a summary dict.

## Analytics Produced

`FinanceAnalytics` in `finops/finance_analytics.py` provides:

| Method | Description |
|---|---|
| `summary(run_id)` | Run-level counters: lines read/valid/rejected, invoices processed/reconciled/blocked, amounts |
| `reconciliation_status_by_store(run_id)` | Line counts and amounts grouped by store and finance state |
| `reconciled_sales_by_store_date(run_id)` | Daily reconciled sale totals per store |
| `blocked_returns(run_id)` | All return lines with state other than RECONCILED, with full traceability |
| `posting_success_failure_counts(run_id)` | Posting outcome counts and total attempt counts |
| `posting_status_by_invoice(run_id)` | Per-invoice posting detail including idempotency key, HTTP status, and error |
| `finance_line_rows(run_id)` | All finance lines as dicts (used for anomaly candidate generation) |
| `posting_rows(run_id)` | All posting records as dicts (used for anomaly candidate generation) |
| `report(run_id)` | Combined dict of all the above |

## Anomaly Integration

### Anomaly Types

| Anomaly Type | Source | Severity | Trigger |
|---|---|---|---|
| `FINANCE_FIELDS_INCOMPLETE` | Finance line | MEDIUM | `finance_state = 'FINANCE_FIELDS_INCOMPLETE'` |
| `FINANCE_TOTAL_MISMATCH` | Finance line | HIGH | `finance_state = 'TOTAL_MISMATCH'` |
| `FINANCE_CONFLICTING_DUPLICATE` | Finance line | HIGH | `finance_state = 'CONFLICTING_DUPLICATE'` |
| `FINANCE_INCOMPLETE_INVOICE` | Finance line | HIGH | `finance_state = 'INCOMPLETE_INVOICE'` |
| `ACCOUNTING_POSTING_FAILURE` | Posting record | HIGH | `posting_status IN ('FAILED', 'PERMANENT_FAILURE', 'RETRYABLE_FAILURE')` |
| `ACCOUNTING_POSTING_TIMEOUT` | Posting record | MEDIUM | `posting_status = 'TIMEOUT'` or `timeout_observed = TRUE` |
| `ACCOUNTING_POSTING_RETRY` | Posting record | MEDIUM | `attempt_count > 1` and status not a failure |

### Traceability

The `anomalies` table does not have dedicated finance foreign-key columns. Traceability is embedded in the `description` field using a structured key=value format:

```
FINANCE_FIELDS_INCOMPLETE|run_id=1|finance_line_id=9|invoice_no=sales_return:5|line_no=501|company_id=1|store_id=2|customer_id=10|product_id=20|sale_id=30|sale_item_id=40|return_id=50|return_item_id=60|reason=missing taxable_value/gst_amount
```

This allows tracing from anomaly → finance line → invoice → sale/return → store → company.

### Idempotency

`persist_finance_anomalies` reads all existing finance anomaly descriptions before inserting. A candidate is skipped if its description already exists. Re-running Phase 5 against the same data inserts 0 new anomalies.

## Live Results (Phase 5 Run)

| Metric | Value |
|---|---|
| Run ID | 1 |
| Finance lines read | 14,985 |
| Anomaly candidates generated | 350 |
| Anomalies inserted (first run) | 350 |
| Anomalies inserted (re-run) | 0 |
| Anomaly type | `FINANCE_FIELDS_INCOMPLETE` |
| Posting failures | 0 |
| Posting retries | 0 |

All 350 anomalies correspond to blocked return lines. No posting failures or retries occurred in the current run.

## Total Anomaly State After Phase 5

| Anomaly Type | Count | Source |
|---|---|---|
| `SALES_SPIKE` | 32 | Deterministic sales rule |
| `LOW_STOCK_WITH_DEMAND` | 23 | Deterministic inventory rule |
| `FINANCE_FIELDS_INCOMPLETE` | 350 | Phase 5 finance integration |
| **Total** | **405** | |

## SQL Analytics Queries

`database/queries/finance.sql` contains 12 queries:

1. Reconciliation run summary
2. Reconciliation state counts for a run
3. Reconciliation status by store
4. Reconciled sales amount by store and date
5. Blocked financial documents (returns) with full traceability
6. Accounting posting success/failure counts
7. Posting status by invoice
8. Posting failures and retries
9. Finance anomaly summary
10. Finance anomaly detail with traceability
11. All anomaly types summary (cross-phase view)
12. Latest reconciliation run (no parameter needed)

## Tests

`tests/test_finance_analytics.py` covers:

- Blocked finance line produces a traceable anomaly with correct type, description fields, and sale_id.
- Posting failure and retry rules produce the correct anomaly types.
- Successful single-attempt posting produces no anomaly.

## What Phase 5 Does Not Do

- Does not modify source sales, returns, or ERP data.
- Does not use LLMs, AI agents, or RAG.
- Does not implement FastAPI endpoints.
- Does not invent missing return-level tax data.
- Does not post blocked returns to the accounting system.
