# Next Steps

## DONE

- Synthetic ERP dataset organized under raw, processed, reference, and quality folders.
- Sales duplicate cleaning script created.
- PostgreSQL schema file created.
- Reference and operational loader scripts created.
- Operational dataset loaded according to the supplied counts.
- Daily store, product, customer, and inventory data products populated according to supplied validation notes.
- Return, customer-spend, and inventory-cutoff reconciliations documented.
- Data-quality and transaction-debugging lessons recorded.

## IN PROGRESS

- Reviewing the live database schema against repository SQL.
- Making data-product generation queries reproducible and easy to rerun.
- Confirming exact behavior of backend, frontend, and AI files.

## TODO: Anomaly Detection

1. Define measurable anomaly rules.
2. Choose source data products.
3. Write detected anomalies to `anomalies`.
4. Test false positives and edge cases.
5. Document severity and status.

## TODO: AI Insights and Actions

1. Add tools that query validated data products.
2. Implement specialist agent workflows.
3. Add policy documents and RAG retrieval.
4. Store explanations in `ai_insights`.
5. Generate reviewed action items in `action_items`.
6. Add audit records before automation.

## TODO: FastAPI

1. Implement `backend/app/main.py`.
2. Connect database sessions safely.
3. Implement route, schema, and service contracts.
4. Add authentication and authorization.
5. Test analytics and operational endpoints.

## TODO: Streamlit

1. Implement `frontend/app.py`.
2. Build dashboard and page navigation.
3. Connect to backend or read-only analytics queries.
4. Add tables, charts, filters, and AI assistant views.

## TODO: LangGraph and RAG

1. Implement supervisor routing.
2. Implement sales, finance, inventory, and anomaly agents.
3. Add tool-call tracing.
4. Add retrieval of business policies.
5. Prevent agents from calculating unsupported totals.

## TODO: Testing and Deployment

- Populate `requirements.txt` with verified dependencies.
- Add reproducible setup instructions.
- Test clean reload behavior.
- Test database constraints and transaction rollback.
- Add API, data-product, and agent workflow tests.
- Move credentials to environment variables.
- Document deployment and monitoring.

## Next Technical Step

The next technical step should be anomaly detection on top of the validated data products. It creates a useful, testable bridge between deterministic analytics and the planned AI explanation layer.

## Interview Takeaway

- Build anomaly detection before asking agents to explain anomalies.
- Add AI only after source data and metrics have validation checks.
- Authentication, audit logs, and review are required before automation.
- A roadmap should distinguish completed work from intended work.
