# Next Steps

## DONE

- Synthetic ERP dataset organized under raw, processed, reference, and quality folders.
- Sales duplicate cleaning script created (`INV-000151` removed from processed data).
- PostgreSQL schema created (33 tables including 3 finance persistence tables).
- Reference and operational loader scripts created.
- Operational dataset loaded: 5,000 sales, 15,067 sale items, 350 returns, 4,854 payments.
- Daily store, product, customer, and inventory data products populated and validated.
- Deterministic anomaly detection: 32 `SALES_SPIKE`, 23 `LOW_STOCK_WITH_DEMAND`.
- Finance reconciliation engine (`finops/`): money, dates, validation, deduplication, reconciliation, posting, retry, idempotency, ledger, journal.
- ERP adapter: reads existing PostgreSQL data without modifying source records.
- Finance persistence: `finance_reconciliation_runs`, `finance_reconciliation_lines`, `accounting_postings`.
- Mock accounting posting: 4,854 sales posted, 0 failures, idempotency verified.
- Finance analytics (`finops/finance_analytics.py`): reconciliation summary, status by store, reconciled sales by store/date, blocked returns, posting counts, posting status by invoice.
- Finance anomaly integration: 350 `FINANCE_FIELDS_INCOMPLETE` anomalies inserted with full traceability. Re-runs are idempotent (0 duplicates).
- `database/queries/finance.sql`: 12 analytics queries covering all Phase 5 analytics.
- 34 tests passing across all phases.

## CURRENT STATE

- 4,854 completed sales reconciled.
- 350 approved returns blocked (`FINANCE_FIELDS_INCOMPLETE`) — return-level tax data unavailable.
- Total anomalies: 405 (32 SALES_SPIKE + 23 LOW_STOCK_WITH_DEMAND + 350 FINANCE_FIELDS_INCOMPLETE).
- No real external accounting API integrated (mock only).
- No FastAPI, Streamlit, LangGraph, or RAG implemented yet.

## NEXT: Phase 6 — FastAPI Backend

Architecture:

```
Route → Pydantic schema → Service → Database → Response
```

Endpoints to implement:

1. `GET /stores` — store list and summary
2. `GET /sales` — sales with filters (store, date, status)
3. `GET /inventory` — inventory levels and metrics
4. `GET /finance/reconciliation` — reconciliation run summary
5. `GET /finance/reconciliation/by-store` — status by store
6. `GET /finance/blocked-returns` — blocked return details
7. `GET /finance/postings` — posting status and counts
8. `GET /anomalies` — anomaly list with filters
9. `GET /analytics/daily-store` — daily store metrics
10. `GET /analytics/product-performance` — product metrics

Implementation order:
1. Implement `backend/app/main.py` with FastAPI app and router registration.
2. Implement database session (`backend/app/database/session.py`).
3. Implement finance routes and service (highest value, already has data).
4. Implement analytics routes.
5. Implement operational routes (sales, inventory, anomalies).
6. Add Pydantic response schemas.
7. Add tests for each route.

## TODO: Phase 7 — RAG System

Build a finance/retail policy knowledge base.

RAG answers questions such as:
- What is the policy for a financial discrepancy?
- What should happen when an invoice fails reconciliation?
- What is the refund policy?
- What should be done for low inventory?

The RAG system provides policy context, not financial calculations.

## TODO: Phase 8 — LangGraph Agentic AI

Supervisor + specialist architecture:

```
User
 ↓
Supervisor Agent
 ↓
 ├── Finance Agent
 ├── Sales Analytics Agent
 ├── Inventory Agent
 ├── Anomaly Investigation Agent
 └── Policy/RAG Agent
 ↓
Verified tools/database results
 ↓
Final grounded response
```

Agents must use tools to query the database rather than invent numbers.

## TODO: Phase 9 — AI Insights and Action Items

Populate `ai_insights`, `action_items`, `automation_runs`.

Example flow:
- Anomaly detected → investigate database → retrieve relevant policy → explain root cause → recommend action → create action item.

## TODO: Phase 10 — Streamlit Frontend

Dashboard consuming the FastAPI backend:
- Revenue, sales, inventory, customers.
- Anomalies and finance reconciliation status.
- Accounting posting status.
- AI insights and action items.
- AI assistant chat interface.

## Interview Takeaway

- Build anomaly detection before asking agents to explain anomalies.
- Add AI only after source data and metrics have validation checks.
- Authentication, audit logs, and review are required before automation.
- A roadmap should distinguish completed work from intended work.
