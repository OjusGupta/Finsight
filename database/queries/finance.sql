-- ============================================================
-- FinSight Phase 5 - Finance Analytics SQL Queries
-- PostgreSQL
-- All queries are parameterised with :run_id where applicable.
-- Replace :run_id with the actual run_id value when executing.
-- ============================================================


-- ------------------------------------------------------------
-- 1. RECONCILIATION RUN SUMMARY
-- Returns the top-level counters for a given reconciliation run.
-- ------------------------------------------------------------

SELECT
    run_id,
    source_system,
    status,
    lines_read,
    lines_valid,
    lines_rejected,
    duplicate_lines_skipped,
    invoices_processed,
    invoices_reconciled,
    invoices_blocked,
    amount_reconciled,
    amount_blocked,
    run_started_at,
    run_completed_at
FROM finance_reconciliation_runs
WHERE run_id = :run_id;


-- ------------------------------------------------------------
-- 2. RECONCILIATION STATE COUNTS FOR A RUN
-- How many finance lines are in each state.
-- ------------------------------------------------------------

SELECT
    finance_state,
    COUNT(*)                        AS line_count,
    COALESCE(SUM(line_total), 0)    AS total_amount
FROM finance_reconciliation_lines
WHERE run_id = :run_id
GROUP BY finance_state
ORDER BY finance_state;


-- ------------------------------------------------------------
-- 3. RECONCILIATION STATUS BY STORE
-- Line counts and amounts grouped by store and finance state.
-- ------------------------------------------------------------

SELECT
    frl.store_id,
    s.store_name,
    frl.finance_state,
    COUNT(*)                        AS line_count,
    COALESCE(SUM(frl.line_total), 0) AS total_amount
FROM finance_reconciliation_lines frl
JOIN stores s ON s.store_id = frl.store_id
WHERE frl.run_id = :run_id
GROUP BY frl.store_id, s.store_name, frl.finance_state
ORDER BY frl.store_id, frl.finance_state;


-- ------------------------------------------------------------
-- 4. RECONCILED SALES AMOUNT BY STORE AND DATE
-- Daily reconciled sale totals per store.
-- ------------------------------------------------------------

SELECT
    frl.store_id,
    s.store_name,
    frl.transaction_date,
    COUNT(DISTINCT frl.invoice_no)   AS invoices_reconciled,
    COALESCE(SUM(frl.line_total), 0) AS reconciled_amount
FROM finance_reconciliation_lines frl
JOIN stores s ON s.store_id = frl.store_id
WHERE frl.run_id = :run_id
  AND frl.finance_state = 'RECONCILED'
  AND frl.doc_type = 'sale'
GROUP BY frl.store_id, s.store_name, frl.transaction_date
ORDER BY frl.store_id, frl.transaction_date;


-- ------------------------------------------------------------
-- 5. BLOCKED FINANCIAL DOCUMENTS (RETURNS)
-- All return lines that could not be reconciled, with full
-- traceability to return, sale, store, product, and company.
-- ------------------------------------------------------------

SELECT
    frl.finance_line_id,
    frl.invoice_no,
    frl.finance_state,
    frl.rejection_reason,
    frl.line_total,
    frl.return_id,
    frl.return_item_id,
    frl.sale_id,
    frl.sale_item_id,
    frl.store_id,
    s.store_name,
    frl.company_id,
    c.company_name,
    frl.product_id,
    p.product_name,
    frl.customer_id,
    frl.transaction_date
FROM finance_reconciliation_lines frl
LEFT JOIN stores   s ON s.store_id   = frl.store_id
LEFT JOIN companies c ON c.company_id = frl.company_id
LEFT JOIN products  p ON p.product_id = frl.product_id
WHERE frl.run_id = :run_id
  AND frl.doc_type = 'sales_return'
  AND frl.finance_state <> 'RECONCILED'
ORDER BY frl.finance_line_id;


-- ------------------------------------------------------------
-- 6. ACCOUNTING POSTING SUCCESS / FAILURE COUNTS
-- Summary of posting outcomes for a run.
-- ------------------------------------------------------------

SELECT
    posting_status,
    COUNT(*)                            AS invoice_count,
    COALESCE(SUM(attempt_count), 0)     AS total_attempts
FROM accounting_postings
WHERE run_id = :run_id
GROUP BY posting_status
ORDER BY posting_status;


-- ------------------------------------------------------------
-- 7. POSTING STATUS BY INVOICE
-- Full posting detail for every invoice in a run.
-- ------------------------------------------------------------

SELECT
    invoice_no,
    doc_type,
    idempotency_key,
    posting_status,
    attempt_count,
    last_http_status,
    last_result,
    timeout_observed,
    external_document_id,
    last_error,
    first_attempt_at,
    last_attempt_at,
    posted_at
FROM accounting_postings
WHERE run_id = :run_id
ORDER BY invoice_no;


-- ------------------------------------------------------------
-- 8. POSTING FAILURES AND RETRIES
-- Invoices that failed permanently or required more than one attempt.
-- ------------------------------------------------------------

SELECT
    ap.invoice_no,
    ap.doc_type,
    ap.posting_status,
    ap.attempt_count,
    ap.last_http_status,
    ap.timeout_observed,
    ap.last_error,
    ap.last_attempt_at
FROM accounting_postings ap
WHERE ap.run_id = :run_id
  AND (
      ap.posting_status IN ('FAILED', 'PERMANENT_FAILURE', 'RETRYABLE_FAILURE', 'TIMEOUT')
      OR ap.attempt_count > 1
  )
ORDER BY ap.attempt_count DESC, ap.invoice_no;


-- ------------------------------------------------------------
-- 9. FINANCE ANOMALY SUMMARY
-- All finance-related anomalies grouped by type and severity.
-- ------------------------------------------------------------

SELECT
    anomaly_type,
    severity,
    COUNT(*)        AS anomaly_count,
    status
FROM anomalies
WHERE anomaly_type LIKE 'FINANCE_%'
   OR anomaly_type LIKE 'ACCOUNTING_POSTING_%'
GROUP BY anomaly_type, severity, status
ORDER BY anomaly_type, severity;


-- ------------------------------------------------------------
-- 10. FINANCE ANOMALY DETAIL WITH TRACEABILITY
-- Individual finance anomalies with store and detection metadata.
-- ------------------------------------------------------------

SELECT
    a.anomaly_id,
    a.anomaly_type,
    a.severity,
    a.status,
    a.description,
    a.detected_value,
    a.expected_value,
    a.store_id,
    s.store_name,
    a.product_id,
    a.sale_id,
    a.detected_at
FROM anomalies a
LEFT JOIN stores s ON s.store_id = a.store_id
WHERE a.anomaly_type LIKE 'FINANCE_%'
   OR a.anomaly_type LIKE 'ACCOUNTING_POSTING_%'
ORDER BY a.anomaly_type, a.anomaly_id;


-- ------------------------------------------------------------
-- 11. ALL ANOMALY TYPES SUMMARY (CROSS-PHASE VIEW)
-- Counts for every anomaly type across all detection phases.
-- ------------------------------------------------------------

SELECT
    anomaly_type,
    severity,
    COUNT(*)    AS anomaly_count,
    status
FROM anomalies
GROUP BY anomaly_type, severity, status
ORDER BY anomaly_type, severity;


-- ------------------------------------------------------------
-- 12. LATEST RECONCILIATION RUN (NO PARAMETER NEEDED)
-- Quick check of the most recent run without knowing run_id.
-- ------------------------------------------------------------

SELECT
    run_id,
    source_system,
    status,
    invoices_reconciled,
    invoices_blocked,
    amount_reconciled,
    amount_blocked,
    run_started_at,
    run_completed_at
FROM finance_reconciliation_runs
ORDER BY run_started_at DESC, run_id DESC
LIMIT 1;
