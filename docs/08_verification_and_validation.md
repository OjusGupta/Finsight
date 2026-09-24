# Verification and Validation

This document records checks supplied from the current development work. Counts are dataset-specific and may change.

## Operational Counts

| Table | Expected/current count | Status |
|---|---:|---|
| companies | 1 | PASS according to supplied loaded counts |
| stores | 5 | PASS according to supplied loaded counts |
| users | 41 | PASS according to supplied loaded counts |
| categories | 8 | PASS according to supplied loaded counts |
| customers | 1000 | PASS according to supplied loaded counts |
| products | 240 | PASS according to supplied loaded counts |
| suppliers | 30 | PASS according to supplied loaded counts |
| supplier_products | 302 | PASS according to supplied loaded counts |
| inventory | 900 | PASS according to supplied loaded counts |
| inventory_movements | 8477 | PASS according to supplied loaded counts |
| sales | 5000 | PASS according to supplied loaded counts |
| sale_items | 15067 | PASS according to supplied loaded counts |
| payments | 4854 | PASS according to supplied loaded counts |
| returns | 350 | PASS according to supplied loaded counts |
| return_items | 350 | PASS according to supplied loaded counts |
| refunds | 350 | PASS according to supplied loaded counts |
| expenses | 180 | PASS according to supplied loaded counts |
| login_events | 2530 | PASS according to supplied loaded counts |

## Duplicate Removal

- Raw sales: 5001
- Processed sales: 5000
- Removed sales: 1
- Raw sale items: 15069
- Processed sale items: 15067
- Removed sale items: 2
- Duplicate invoice: `INV-000151`

Status: PASS according to the cleaning-script results supplied for this project. A fresh rerun is **To be verified**.

## Product Performance Reconciliation

| Check | Expected/result |
|---|---:|
| Rows | 12643 |
| Units sold | 36517 |
| Revenue | 906892826.98 |
| Units returned | 584 |
| Return amount | 11894830.08 |

The return totals matched direct return and return-item totals. Status: PASS according to supplied validation notes.

## Customer Spend Reconciliation

`customer_metrics.total_spent` was compared with completed sales having a non-null customer:

```text
SUM(sales.total_amount) = 3327460247.73
customer_metrics.total_spent = 3327460247.73
```

Status: PASS according to supplied validation notes.

## Inventory Reconciliation

| Check | Result |
|---|---:|
| Inventory metric rows | 6174 |
| Distinct inventory records | 900 |
| Units sold | 13461 |
| Units received | 35145 |
| Units returned | 402 |
| Stock value | 5417030896.18 |
| Date range | 2026-04-01 to 2026-09-15 |

The movement source contained 700 purchase rows and 7777 sale rows. Applying the `activity date <= inventory.last_updated date` cutoff produced 5356 matched sales rows / 13461 units and 240 return items / 402 units.

Status: PASS for the stated cutoff definition according to supplied validation notes. Exact live query text is **To be verified**.

## Return Join Check

The intended safe join is:

```text
return_items.sale_item_id
    -> sale_items.sale_item_id
    -> sale_items.product_id

returns.sale_id
    -> sales.sale_id
    -> sales.store_id
```

Return quantities must be aggregated once by the required inventory key and date. Status: NOTE; exact executed query is **To be verified**.

## Schema Checks

The repository schema defines `inventory.last_updated`, while the raw inventory CSV uses `updated_at`. Status: PASS for the repository schema inspection. Always verify the live database before execution.

## Transaction Rollback

A failed statement caused PostgreSQL error `25P02` on later statements because the transaction was aborted. `ROLLBACK;` was used to clear the failed transaction. Status: PASS according to the development record.

## Inventory Balance Caveat

A validation query found mismatches for many inventory IDs when trying to infer historical opening stock from current quantity and movements. The failed validation message was mistakenly cast to integer, causing error `22P02`. This is a debugging issue, not proof that all historical balances are valid.

The safe rule is: do not use `GREATEST(0, ...)` to hide an inconsistent negative balance. Add genuine opening-stock information, correct the source data, exclude invalid histories, or document the mismatch.

## Interview Takeaway

- A validation must state its expected result and evidence.
- Reconciliation is stronger than checking only row counts.
- A transaction error requires rollback before continuing.
- A loaded table can still contain incorrect business logic.
