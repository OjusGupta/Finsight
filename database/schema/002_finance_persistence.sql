-- FinSight Phase 4 finance reconciliation and accounting posting persistence

CREATE TABLE IF NOT EXISTS finance_reconciliation_runs (
    run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_system VARCHAR(100) NOT NULL,
    run_started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    run_completed_at TIMESTAMP,
    status VARCHAR(40) NOT NULL DEFAULT 'RUNNING',
    lines_read INT NOT NULL DEFAULT 0,
    lines_valid INT NOT NULL DEFAULT 0,
    lines_rejected INT NOT NULL DEFAULT 0,
    duplicate_lines_skipped INT NOT NULL DEFAULT 0,
    invoices_processed INT NOT NULL DEFAULT 0,
    invoices_reconciled INT NOT NULL DEFAULT 0,
    invoices_blocked INT NOT NULL DEFAULT 0,
    amount_reconciled NUMERIC(18,2) NOT NULL DEFAULT 0,
    amount_blocked NUMERIC(18,2) NOT NULL DEFAULT 0,
    summary_json JSONB,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_finance_run_status
        CHECK (status IN ('RUNNING', 'COMPLETED', 'COMPLETED_WITH_BLOCKS', 'FAILED')),
    CONSTRAINT chk_finance_run_counts
        CHECK (
            lines_read >= 0 AND lines_valid >= 0 AND lines_rejected >= 0
            AND duplicate_lines_skipped >= 0 AND invoices_processed >= 0
            AND invoices_reconciled >= 0 AND invoices_blocked >= 0
        ),
    CONSTRAINT chk_finance_run_amounts
        CHECK (amount_reconciled >= 0 AND amount_blocked >= 0)
);

CREATE TABLE IF NOT EXISTS finance_reconciliation_lines (
    finance_line_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id BIGINT NOT NULL,
    source_table VARCHAR(50) NOT NULL,
    source_id BIGINT NOT NULL,
    company_id INT,
    store_id INT,
    customer_id INT,
    product_id INT,
    sale_id INT,
    sale_item_id INT,
    return_id INT,
    return_item_id INT,
    invoice_no VARCHAR(100) NOT NULL,
    line_no VARCHAR(100) NOT NULL,
    doc_type VARCHAR(30) NOT NULL,
    transaction_date DATE NOT NULL,
    customer_code VARCHAR(100),
    line_total NUMERIC(18,2) NOT NULL,
    taxable_value NUMERIC(18,2),
    gst_amount NUMERIC(18,2),
    finance_state VARCHAR(50) NOT NULL,
    rejection_reason VARCHAR(100),
    posting_allowed BOOLEAN NOT NULL DEFAULT FALSE,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_finance_line_run
        FOREIGN KEY (run_id) REFERENCES finance_reconciliation_runs(run_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_finance_line_company
        FOREIGN KEY (company_id) REFERENCES companies(company_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_finance_line_store
        FOREIGN KEY (store_id) REFERENCES stores(store_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_finance_line_customer
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_finance_line_product
        FOREIGN KEY (product_id) REFERENCES products(product_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_finance_line_sale
        FOREIGN KEY (sale_id) REFERENCES sales(sale_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_finance_line_sale_item
        FOREIGN KEY (sale_item_id) REFERENCES sale_items(sale_item_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_finance_line_return
        FOREIGN KEY (return_id) REFERENCES returns(return_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_finance_line_return_item
        FOREIGN KEY (return_item_id) REFERENCES return_items(return_item_id)
        ON DELETE RESTRICT,
    CONSTRAINT uq_finance_line_source
        UNIQUE (run_id, source_table, source_id),
    CONSTRAINT chk_finance_line_source
        CHECK (source_table IN ('sale_items', 'return_items')),
    CONSTRAINT chk_finance_line_doc_type
        CHECK (doc_type IN ('sale', 'sales_return')),
    CONSTRAINT chk_finance_line_signed_amount
        CHECK (
            (doc_type = 'sale' AND line_total > 0)
            OR (doc_type = 'sales_return' AND line_total < 0)
        ),
    CONSTRAINT chk_finance_line_state
        CHECK (
            finance_state IN (
                'STRUCTURALLY_VALID', 'FINANCE_FIELDS_INCOMPLETE',
                'RECONCILED', 'TOTAL_MISMATCH', 'INCOMPLETE_INVOICE',
                'CONFLICTING_DUPLICATE', 'REJECTED'
            )
        ),
    CONSTRAINT chk_finance_line_posting
        CHECK (posting_allowed = FALSE OR finance_state = 'RECONCILED')
);

CREATE TABLE IF NOT EXISTS accounting_postings (
    posting_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id BIGINT NOT NULL,
    invoice_no VARCHAR(100) NOT NULL,
    doc_type VARCHAR(30) NOT NULL,
    idempotency_key VARCHAR(150) NOT NULL,
    reconciliation_state VARCHAR(50) NOT NULL,
    posting_status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    attempt_count INT NOT NULL DEFAULT 0,
    external_document_id VARCHAR(150),
    last_http_status INT,
    last_result VARCHAR(50),
    last_error TEXT,
    timeout_observed BOOLEAN NOT NULL DEFAULT FALSE,
    attempt_history JSONB NOT NULL DEFAULT '[]'::jsonb,
    first_attempt_at TIMESTAMP,
    last_attempt_at TIMESTAMP,
    posted_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_accounting_posting_run
        FOREIGN KEY (run_id) REFERENCES finance_reconciliation_runs(run_id)
        ON DELETE RESTRICT,
    CONSTRAINT uq_accounting_posting_idempotency
        UNIQUE (idempotency_key),
    CONSTRAINT chk_accounting_posting_doc_type
        CHECK (doc_type IN ('sale', 'sales_return')),
    CONSTRAINT chk_accounting_posting_reconciliation
        CHECK (reconciliation_state = 'RECONCILED'),
    CONSTRAINT chk_accounting_posting_status
        CHECK (
            posting_status IN (
                'PENDING', 'POSTING', 'POSTED', 'ALREADY_POSTED',
                'TIMEOUT', 'RETRYABLE_FAILURE', 'PERMANENT_FAILURE', 'FAILED'
            )
        ),
    CONSTRAINT chk_accounting_posting_attempts
        CHECK (attempt_count >= 0 AND attempt_count <= 3),
    CONSTRAINT chk_accounting_posting_http_status
        CHECK (last_http_status IS NULL OR (last_http_status BETWEEN 100 AND 599))
);

CREATE INDEX IF NOT EXISTS idx_finance_runs_status_date
    ON finance_reconciliation_runs (status, run_started_at);
CREATE INDEX IF NOT EXISTS idx_finance_lines_run_state
    ON finance_reconciliation_lines (run_id, finance_state);
CREATE INDEX IF NOT EXISTS idx_finance_lines_invoice
    ON finance_reconciliation_lines (invoice_no);
CREATE INDEX IF NOT EXISTS idx_finance_lines_source
    ON finance_reconciliation_lines (source_table, source_id);
CREATE INDEX IF NOT EXISTS idx_finance_lines_store_date
    ON finance_reconciliation_lines (store_id, transaction_date);
CREATE INDEX IF NOT EXISTS idx_finance_lines_customer_date
    ON finance_reconciliation_lines (customer_id, transaction_date);
CREATE INDEX IF NOT EXISTS idx_finance_lines_product_date
    ON finance_reconciliation_lines (product_id, transaction_date);
CREATE INDEX IF NOT EXISTS idx_accounting_postings_run_status
    ON accounting_postings (run_id, posting_status);
CREATE INDEX IF NOT EXISTS idx_accounting_postings_invoice
    ON accounting_postings (invoice_no);
CREATE INDEX IF NOT EXISTS idx_accounting_postings_external_id
    ON accounting_postings (external_document_id);
