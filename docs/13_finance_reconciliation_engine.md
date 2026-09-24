# Finance Reconciliation Engine

## Scope

This phase implements deterministic finance reconciliation and a FinSight-specific read-only ERP adapter as reusable Python modules. It does not implement accounting posting, AI, RAG, FastAPI, Streamlit, LangGraph, or PostgreSQL persistence tables.

The engine accepts assignment-shaped line exports with fields such as `invoice_no`, `line_no`, `doc_type`, `transaction_date`, `customer_code`, `line_total`, `taxable_value`, and `gst_amount`.

The existing FinSight business entities are reused through the PostgreSQL adapter. The adapter preserves operational IDs and does not create duplicate sales, returns, customers, stores, products, or invoices.

## Business Flow

```text
FinSight PostgreSQL ERP data
  -> read-only ERP adapter
  -> normalization
    -> line validation
    -> duplicate detection
    -> invoice grouping
    -> invoice reconciliation
    -> accounting posting
    -> retry and timeout handling
    -> posted ledger and journal
    -> JSON report
```

## Validation Rules

- Money uses `Decimal`, not binary floating point.
- Money is quantized to two decimals with `ROUND_HALF_UP`.
- Accepted amount forms include plain decimal, Indian grouping, `Rs.` prefix, parenthesized negative, and trailing-minus negative values.
- Invalid amounts produce `bad_amount`.
- Accepted dates are `DD-MM-YYYY`, `DD/MM/YYYY`, and `YYYY-MM-DD`.
- Slash dates are day-first.
- Invalid dates produce `bad_date`.
- Dates later than the run date produce `future_date`.
- Only `sale` and `sales_return` are accepted document types.
- Sales require positive line totals; returns require negative line totals.
- Sign violations produce `sign_mismatch`.

## Duplicate and Invoice Rules

Duplicate identity is `(invoice_no, line_no)`.

- Identical duplicates keep one row and increment `duplicate_lines_skipped`.
- Conflicting duplicates reject every row with `conflicting_duplicate`.
- Customer codes are normalized with trim and uppercase.
- Unknown customers resolve to `UNKNOWN` and increment `invoices_unknown_customer`.
- Invoices are rejected as a whole when any line is invalid.
- Partial invoices are never posted.

Invoice reconciliation calculates:

```text
invoice_total = SUM(line_total)
comparison_total = SUM(taxable_value + gst_amount)
tolerance = 0.05 * number_of_lines
```

An invoice is rejected with `total_mismatch` when the absolute difference exceeds the tolerance.

## Accounting API Behavior

The standard-library client sends `Idempotency-Key: invoice_no`.

| Response | Behavior |
|---|---|
| `201` | Successful posting |
| `409` | Already posted; treated as successful |
| `422` | Permanent failure; no retry |
| `500`/`503` | Retryable failure |
| Timeout | Retryable; the write may already have succeeded |

There are at most three total attempts. Retries always reuse the invoice number as the idempotency key.

## Ledger and Journal

The default posted ledger is `state/posted_ledger.json`. An invoice present in the ledger is not posted again and increments `invoices_skipped_already_posted`.

The default posting journal is `state/posting_journal.json`. It records invoice number, attempt, timestamp, result, HTTP status when available, and final/retry outcome. It does not store credentials.

Ledger and journal writes use temporary files and `os.replace` to reduce corruption risk during process termination.

## Report and Exit Codes

The report uses the exact required fields and formats money as strings with two decimals:

```json
{
  "run_date": "YYYY-MM-DD",
  "lines_read": 0,
  "duplicate_lines_skipped": 0,
  "lines_rejected": 0,
  "lines_valid": 0,
  "invoices_seen": 0,
  "invoices_posted": 0,
  "invoices_skipped_already_posted": 0,
  "invoices_failed": 0,
  "invoices_rejected": 0,
  "invoices_unknown_customer": 0,
  "amount_posted": "0.00",
  "sales_amount_posted": "0.00",
  "returns_amount_posted": "0.00",
  "amount_rejected": "0.00",
  "rejects": [],
  "rejected_invoices": [],
  "failures": []
}
```

The engine validates both reconciliation identities:

```text
lines_read = duplicate_lines_skipped + lines_valid + lines_rejected
invoices_seen = invoices_posted + invoices_skipped_already_posted + invoices_failed + invoices_rejected
```

Exit codes are:

- `0`: no invoice posting failure.
- `1`: at least one invoice posting failure.
- `2`: the job could not run.

Rejected invoices alone do not produce exit code `1`.

## FinSight ERP Tax Mapping

The FinSight ERP adapter reads `sale_items.tax_amount` after the verified database migration. This column stores the source dataset's original `sale_items.csv.tax` value, matched by `sale_item_id`.

For sale lines, the verified arithmetic is:

```text
taxable_value = unit_price * quantity - discount_amount
gst_amount = tax_amount
taxable_value + gst_amount = line_total
```

The source dataset's `sale_items.csv.tax` value was verified against all 15,067 processed sale-item rows and preserved in PostgreSQL as `sale_items.tax_amount`. The adapter maps this `tax_amount` to the engine's tax component for sale-line reconciliation. This documentation does not claim that the source field is legally or officially GST. Return lines remain finance-incomplete until return-level tax data is available.

## Live FinSight Verification

The read-only adapter and reconciliation integration produced:

- 4,854 completed sales reconciled.
- 14,635 normalized sale lines.
- 350 approved returns extracted.
- 350 normalized return lines.
- 5,204 invoice groups processed.
- 4,854 invoice groups eligible for complete reconciliation.
- 350 return groups blocked with `FINANCE_FIELDS_INCOMPLETE`.

The blocked return state is intentional. Return-level `taxable_value` and `gst_amount` are not available, so returns are not labeled reconciled and are not eligible for posting.

## CLI

```text
python pipeline.py \
  --lines <csv> \
  --customers <csv> \
  --run-date YYYY-MM-DD \
  [--ledger PATH] \
  [--journal PATH] \
  [--report PATH]
```

When no injected client is supplied, the CLI expects `ACCOUNTING_API_URL`. Tests use a deterministic fake client and never call an external service.

## Testing

The focused suite contains 23 passing tests covering money formats, date formats, future dates, sign validation, identical and conflicting duplicates, customer resolution, tolerance, partial invoices, HTTP statuses, retry limits, timeout reuse of idempotency keys, rerun ledger skipping, journal creation, report shape, adapter traceability, tax restoration, live-shaped integration states, and reconciliation identities.

## PostgreSQL and Later Phases

The adapter reads existing PostgreSQL operational data, while Phase 4 persists reconciliation and mock-posting results in:

- `finance_reconciliation_runs`
- `finance_reconciliation_lines`
- `accounting_postings`

Existing FinSight operational entities remain the source of truth. The accounting client used for current validation is local and deterministic; no real external accounting system is integrated.

Phase 4 behavior verified against the live database:

- One run persisted with status `COMPLETED_WITH_BLOCKS`.
- 14,985 finance lines persisted.
- 4,854 eligible sales posted to the local mock client.
- 350 return groups remained `FINANCE_FIELDS_INCOMPLETE`.
- No return posting records were created.
- Invoice identity is the accounting idempotency key.
- Retry and timeout behavior remains capped at three total attempts.

The persistence migration is [002_finance_persistence.sql](../database/schema/002_finance_persistence.sql). It does not duplicate operational sales, returns, customers, stores, or products.

Anomaly detection, AI insights, agents, RAG, FastAPI, and frontend integration require separate design and review.
