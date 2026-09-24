# Data Products

A **data product** is a reusable table of derived business information. Its **grain** is what one row represents, such as one store-day or one product-day.

## `daily_store_metrics`

### Purpose
Summarizes store performance by day.

### Sources and calculations

The schema contains store, sales, returns, and expense relationships. The documented definition is:

```text
net_sales = total_sales - total_returns
```

Returns reach stores through `returns -> sales -> sales.store_id`. Expenses remain tracked separately.

### Grain and status

Grain: store-day. Current rows: 905, according to the supplied project validation notes. Exact generation SQL is **To be verified**.

### Limitations

The supplied definition describes net sales but not every filtering rule. The status is **NOTE: verified aggregate supplied, full query to be verified**.

## `product_performance`

### Purpose
Summarizes sales and returns by product and date.

### Sources and calculations

Sources include sales, sale items, returns, return items, and products. Documented totals are:

- Rows: 12643
- Units sold: 36517
- Revenue: 906892826.98
- Units returned: 584
- Return amount: 11894830.08

### Grain and validation

Grain: product-day. The return values reconcile with 350 direct returns, 350 return items, 584 returned units, and refund amount 11894830.08.

### Limitations

The exact live generation query is **To be verified**.

## `customer_metrics`

### Purpose
Summarizes customer spending, purchased items, and returns.

### Sources and calculations

Sources include customers, sales, sale items, returns, and return items. Documented totals are:

- Rows: 5111
- Total spent: 3327460247.73
- Total items purchased: 36517
- Total returns: 584
- Total refund amount: 11894830.08

### Validation

`total_spent` matched `SUM(sales.total_amount)` for completed sales with a non-null customer: 3327460247.73.

### Grain and limitations

Grain: customer-day. The exact live generation query is **To be verified**.

## `inventory_metrics`

### Purpose
Tracks daily inventory movement, stock quantities, value, and status.

### Sources and calculations

Sources include inventory, products, inventory movements, sales-related returns, and return items. The documented status values are `LOW_STOCK`, `NORMAL`, and potentially `OUT_OF_STOCK` or `OVERSTOCKED` when applicable.

Current supplied results:

- Rows: 6174
- Distinct inventory records: 900
- Date range: 2026-04-01 to 2026-09-15
- Units sold: 13461
- Units received: 35145
- Units returned: 402
- Stock value: 5417030896.18
- `LOW_STOCK`: 572
- `NORMAL`: 5602
- `OUT_OF_STOCK`: 0

The movement cutoff was activity date less than or equal to `inventory.last_updated`. Matching produced 5356 sales rows and 13461 units, plus 240 return items and 402 units.

### Return safety

Return items must be aggregated after joining through `sale_items` for product and through `sales` for store. Pre-aggregation by inventory and date prevents a return quantity from being multiplied by unrelated joins.

### Balance limitation

Historical opening stock is not always directly represented. If movement history cannot reconcile exactly with current inventory quantity without negative balances, the mismatch must be reported, not hidden with `GREATEST(0, ...)`.

## Decision

**Decision:** Validate each data product against direct source totals.

**Why:** Derived tables can be wrong even when they load successfully.

**Alternative:** Trust row insertion as proof of correctness.

**Reason:** Successful insertion proves only schema compatibility, not business correctness.

## Interview Takeaway

- Grain tells you what one row means.
- Reconciliation compares a derived result with an independent calculation.
- Joins can silently multiply amounts.
- Inventory balance history needs an explicit opening-stock assumption.
