# FinSight - Agentic Finance & Retail Operations Intelligence Platform

FinSight is a retail and finance operations intelligence project. It loads ERP-style CSV data into PostgreSQL, cleans and validates the source data, creates repeatable analytics data products, and is intended to add anomaly detection, AI agents, retrieval-augmented generation (RAG), and recommended business actions.

## Problem

Retail teams often have sales, inventory, customer, payment, return, and expense information in separate operational records. FinSight brings those records together so that calculations are reproducible and business questions can eventually be answered with database evidence instead of guesses.

## Current Status

The dataset, PostgreSQL loading work, ERP finance adapter, and deterministic finance reconciliation engine are the most concrete parts of the repository. The current live integration reconciles 4,854 completed sales. The 350 approved returns are extracted and preserved but remain blocked because return-level tax fields are not available. Backend, frontend, and AI entry-point files exist, but several are currently empty; those layers remain planned.

## Architecture

```text
ERP-style CSV data
	|
	v
Raw data -> cleaning and validation -> processed CSV
				      |
				      v
			      PostgreSQL database
				      |
				      v
			  Analytics data products
				      |
				      v
		    anomalies -> agents -> RAG -> actions
```

Deterministic SQL and Python should calculate financial and inventory numbers. LLMs should interpret verified results, explain findings, combine them with policy documents, and recommend actions.

## Technology

- Python for cleaning, loading, and planned application logic
- PostgreSQL and pgAdmin for relational storage and SQL analysis
- FastAPI as the planned backend API
- Streamlit as the planned dashboard layer
- LangGraph as the planned agent workflow framework
- RAG (retrieval-augmented generation) for business-policy context

The repository currently contains `psycopg2`-based loader and read-only adapter code. `requirements.txt` currently lists `pandas` and `psycopg2-binary`; future application dependencies remain **To be verified**.

## Repository Layout

```text
data/       raw, processed, reference, and quality CSV data
database/   schema, seed SQL, and analytics query files
scripts/    cleaning, loading, and setup scripts
backend/    planned API structure: routes, services, models, schemas
frontend/   planned Streamlit pages and reusable components
ai/         planned agents, tools, prompts, RAG, and workflows
docs/       project, database, pipeline, validation, and development notes
tests/      project and backend test locations
```

See [docs/02_architecture.md](docs/02_architecture.md) and [docs/11_development_log.md](docs/11_development_log.md) for the detailed explanation.

## Data Pipeline

1. Keep the original files under `data/.../raw`.
2. Clean the duplicate sales invoice into `data/.../processed/sales`.
3. Load reference and operational data into the `finsight` PostgreSQL database.
4. Build daily store, product, customer, and inventory data products.
5. Validate totals against direct source-table queries.
6. Add anomaly detection and the planned AI/action layers.

The raw dataset is intentionally preserved. The processed copy makes the cleaning decision reproducible and auditable.

## Database

The database is named `finsight`. Core operational entities include companies, stores, users, products, inventory, movements, sales, sale items, payments, returns, return items, refunds, expenses, and login events. Analytics and AI-oriented tables are also defined in the schema. See [docs/03_database_design.md](docs/03_database_design.md).

## Running Later

The repository contains loader scripts and a finance-engine CLI, but there is no verified single end-to-end ERP-to-application command because `scripts/run_pipeline.py`, `backend/app/main.py`, and `frontend/app.py` are currently empty. Use the documented scripts only after checking the local PostgreSQL connection configuration. See [docs/07_database_loading.md](docs/07_database_loading.md).

## Limitations

- Some planned application entry points are empty.
- The supplied data-product counts are environment-specific and may change after reloads.
- Historical inventory balances can be difficult to reconstruct when opening stock is absent or movements are inconsistent.
- Source quality issues remain documented rather than silently corrected.
- Deployment, authentication behavior, and installed dependencies are not fully verified.

## Finance Reconciliation Engine

FinSight includes a deterministic finance reconciliation engine and a read-only ERP adapter. The adapter reads existing sales, sale items, returns, return items, customers, stores, companies, and products without duplicating business entities. It preserves `customer_id` and source IDs, reads the verified `sale_items.tax_amount` field, and maps the source dataset tax into the engine's tax component. This field is not claimed to be legally or officially GST.

The current live result is:

- 4,854 completed sales reconciled.
- 350 approved returns extracted but blocked because return-level tax fields are unavailable.
- No accounting posting or persistence-table integration yet.

Run it with:

```text
python pipeline.py --lines <csv> --customers <csv> --run-date YYYY-MM-DD [--ledger PATH] [--journal PATH] [--report PATH]
```

The engine is independent of PostgreSQL and external AI services. PostgreSQL persistence, anomaly workflows, AI agents, RAG, FastAPI, and the dashboard remain later phases.

## Roadmap

1. Build and validate anomaly detection.
2. Populate AI insights and action items from verified evidence.
3. Implement the FastAPI backend and authentication.
4. Implement the Streamlit dashboard.
5. Implement LangGraph agents and RAG policy retrieval.
6. Expand automated tests and deployment documentation.

## Documentation

- [Project overview](docs/01_project_overview.md)
- [Architecture](docs/02_architecture.md)
- [Database design](docs/03_database_design.md)
- [Data pipeline](docs/04_data_pipeline.md)
- [Data quality and fixes](docs/05_data_quality_and_fixes.md)
- [Data products](docs/06_data_products.md)
- [Database loading](docs/07_database_loading.md)
- [Verification and validation](docs/08_verification_and_validation.md)
- [AI agent design](docs/09_ai_agent_design.md)
- [API design](docs/10_api_design.md)
- [Development log](docs/11_development_log.md)
- [Next steps](docs/12_next_steps.md)
