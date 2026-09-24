# Data Pipeline

## Flow

```text
Raw CSV
   -> cleaning and validation
   -> processed CSV
   -> loader scripts
   -> PostgreSQL
   -> data products
   -> validation
```

## Dataset

The project uses `FinSight_synthetic_ERP_dataset_v1`. Important folders are:

- `raw/sales`: sales, sale items, returns, return items, refunds, and payments
- `raw/inventory`: inventory and inventory movements
- `raw/expenses`: expenses
- `raw/customers`: login events
- `reference`: companies, stores, users, customers, products, categories, suppliers, and supplier products
- `processed/sales`: cleaned sales and sale items
- `quality`: anomaly manifest

## Why Preserve Raw Data

Raw data is evidence of what the source system supplied. Overwriting it would make it difficult to explain what changed. The cleaning script creates a separate processed copy instead.

## Sales Cleaning

The cleaning script:

1. Reads raw `sales.csv`.
2. Drops duplicate `invoice_number` values while keeping the first occurrence.
3. Uppercases sales status.
4. Keeps sale items whose `sale_id` remains in cleaned sales.
5. Writes processed `sales.csv` and `sale_items.csv`.

The supplied dataset result was 5001 original sales, 5000 cleaned sales, 15069 original sale items, and 15067 cleaned sale items. These counts may change if the source data changes.

## Loading

The seed loader reads reference files and inserts records with `ON CONFLICT DO NOTHING` for the relevant keys. The remaining loader reads processed sales and raw operational files. It explicitly maps fields where source and target names differ.

## Data Products

After loading, SQL/Python work creates:

- `daily_store_metrics`
- `product_performance`
- `customer_metrics`
- `inventory_metrics`

The exact creation scripts are not all present in the inspected query files, so implementation details for each generation step are **To be verified**. Validated results are recorded in [08_data_products](06_data_products.md) and [08_verification_and_validation](08_verification_and_validation.md).

## Decision

**Decision:** Separate raw and processed data.

**Why:** Cleaning becomes reproducible and auditable.

**Alternative:** Edit the raw CSV directly.

**Reason:** That would destroy the source record and make the transformation harder to explain.

## Interview Takeaway

- ETL means extract, transform, and load.
- A processed copy is safer than mutating raw evidence.
- Loader mappings are part of data engineering, not cosmetic renaming.
- Every data product should have a documented source and grain.
