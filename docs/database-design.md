\# Database Design

## Why PostgreSQL

PostgreSQL provides tables, relationships, constraints, transactions, and SQL aggregation. These features are useful for ERP data because financial and inventory calculations need consistent, queryable records.

## Database

The project database is `finsight`. The schema file defines operational tables, data-quality tables, analytics data products, and AI/automation tables.

### Operational Tables

`companies`, `stores`, `users`, `categories`, `products`, `suppliers`, `supplier_products`, `customers`, `inventory`, `inventory_movements`, `sales`, `sale_items`, `payments`, `returns`, `return_items`, `refunds`, `expenses`, and `login_events` store business events and master data.

### Data and Analytics Tables

`raw_data_batches`, `raw_sales`, and `data_quality_issues` support ingestion and quality tracking. `daily_store_metrics`, `product_performance`, `customer_metrics`, and `inventory_metrics` are analytics data products.

### AI and Automation Tables

The schema also defines `anomalies`, `ai_insights`, `action_items`, `automation_runs`, and `audit_logs`. Their complete runtime population is **To be verified**.

## Relationship Overview

```text
companies 1---many stores 1---many users
stores 1---many sales 1---many sale_items many---1 products
sales 1---many payments
sales 1---many returns 1---many return_items
return_items many---1 sale_items
stores 1---many inventory many---1 products
inventory 1---many inventory_movements
stores 1---many expenses
```

The return path is important: a return item reaches its product through `return_items.sale_item_id -> sale_items.sale_item_id -> sale_items.product_id`. A return reaches its store through `returns.sale_id -> sales.sale_id -> sales.store_id`.

## Beginner Terms

- A **primary key** uniquely identifies one row, such as `product_id`.
- A **foreign key** points to a row in another table, such as `sales.store_id` pointing to `stores.store_id`.
- A **one-to-many relationship** means one parent can have many child rows, such as one sale having many sale items.
- A **constraint** is a database rule, such as a nonnegative quantity check.
- A **transaction** groups changes so they can be committed together or rolled back after an error.

## Important Inventory Detail

The repository schema uses `inventory.last_updated`, not `updated_at`. Any SQL must be aligned with the actual database before execution; the earlier `updated_at` reference was a documented implementation mistake.

## Decisions

**Decision:** Keep operational facts normalized and create separate data products.

**Why:** It avoids repeating source facts and makes metric grain explicit.

**Alternative:** Calculate every dashboard number directly from raw tables.

**Reason:** Reusable data products make validation and downstream use simpler.

## Interview Takeaway

- Foreign keys protect relationships between business entities.
- Normalization reduces duplicated facts.
- Analytics tables should document their grain and calculation rules.
- Transactions matter when a failed SQL statement must be rolled back.
