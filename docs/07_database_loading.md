# Database Loading

## Database Setup

The target PostgreSQL database is `finsight`, accessed through pgAdmin during development. The repository contains `database/schema/001_initial_schema.sql` and loader scripts. `scripts/setup_database.py` is currently empty, so a complete automated setup command is **To be verified**.

## Loader Scripts

### `scripts/seed_database.py`

This loader reads reference files and inventory data. It uses `psycopg2`, explicit insert column lists, and `ON CONFLICT (id) DO NOTHING` in the inspected functions.

### `scripts/load_remaining_database(1).py`

This loader reads processed sales and sale items, then raw payments, returns, return items, refunds, expenses, and login events. It normalizes values before insertion and prints table counts during verification.

### Cleaning Before Loading

Run the sales cleaning step before the remaining loader because the remaining loader reads:

```text
data/FinSight_synthetic_ERP_dataset_v1/processed/sales/sales.csv
data/FinSight_synthetic_ERP_dataset_v1/processed/sales/sale_items.csv
```

## Source-to-Target Mapping

Examples:

- Source sales `discount` is inserted into target `discount_amount`.
- Source expense `category` maps to target `expense_category`.
- Source inventory CSV `updated_at` maps to the database column `last_updated` in the repository schema.
- Source login `logout_time` has no matching normalized target column; handling is **To be verified**.

## Status Normalization

Refund source statuses are normalized as follows:

```text
SUCCESS    -> COMPLETED
PROCESSED  -> COMPLETED
COMPLETED  -> COMPLETED
PENDING    -> PENDING
FAILED     -> FAILED
```

This gives the database one vocabulary for equivalent business states.

## Conflict Handling

Several loaders use `ON CONFLICT DO NOTHING`. This prevents a repeated load from inserting the same primary key again, but it can also leave an existing row unchanged. Reload semantics should therefore be understood before running a loader twice.

## Loading Order

The relationship order should respect foreign keys:

1. Companies and stores
2. Users, categories, customers, and products
3. Suppliers and supplier products
4. Inventory and inventory movements
5. Sales and sale items
6. Payments, returns, return items, refunds, and expenses
7. Login events
8. Data products and validations

The exact single-command orchestration is **To be verified** because the pipeline script is empty.

## Current Supplied Counts

The loaded dataset notes report:

```text
companies 1          stores 5             users 41
categories 8         customers 1000      products 240
suppliers 30         supplier_products 302
inventory 900        inventory_movements 8477
sales 5000           sale_items 15067    payments 4854
returns 350          return_items 350    refunds 350
expenses 180         login_events 2530
```

These counts describe the current loaded dataset and may change after reloads or corrections.

## Security Note

The inspected loader contains a database password directly in Python source. This is a development risk. Credentials should be moved to environment configuration before deployment. The correct production configuration is **To be verified**.

## Interview Takeaway

- Load parent tables before child tables.
- Explicit insert columns prevent accidental positional mapping.
- `ON CONFLICT DO NOTHING` is idempotent for duplicates but not a full synchronization strategy.
- Never commit real database credentials to source control.
