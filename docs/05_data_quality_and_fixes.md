# Data Quality and Fixes

This is a chronological problem and solution log. A source-data issue is not automatically corrected; it must be recorded and handled deliberately.

## Duplicate Invoice `INV-000151`

### Problem
The raw sales data contained duplicate invoice `INV-000151`, involving sale IDs 151 and 5001.

### Why it happened
The source dataset contained the same transaction information more than once.

### Impact
Loading both rows could violate the unique invoice rule or double-count sales.

### Fix
The cleaning script keeps the first duplicate invoice and writes a processed copy. The raw file is preserved.

### Verification
The supplied counts changed from 5001 to 5000 sales and from 15069 to 15067 sale items.

### Lesson
Deduplication must use a business key such as invoice number and must be auditable.

## Duplicate Sale Items and Movement References

### Problem
The duplicate sale IDs had related duplicate sale items and inventory movement references.

### Why it happened
Removing a duplicated parent sale does not automatically prove that every child event is consistent.

### Impact
Sales, inventory, and return totals could be inflated or linked to the wrong transaction.

### Fix
The processed sale-item file keeps only items whose sale ID remains in cleaned sales. Movement-reference consistency must be checked separately.

### Verification
The processed item count decreased by two. A complete movement-reference reconciliation is **To be verified**.

### Lesson
ERP data must be checked across relationships, not only row by row.

## Classic Shampoo 009 Category

### Problem
Classic Shampoo 009 was categorized as Electronics.

### Why it happened
This is a source data quality issue in the synthetic dataset.

### Impact
Category-based reports can be misleading.

### Fix
The issue is documented. No silent correction is claimed because repository evidence does not show that the source value was changed.

### Verification
A corrected category value is **To be verified**.

### Lesson
A data-quality issue should be visible and traceable rather than silently overwritten.

## `BANK_TRANSFER` Payment Constraint

### Problem
The source contained `BANK_TRANSFER`, but the original payment-method constraint did not allow it.

### Why it happened
The source domain was broader than the initial database constraint.

### Impact
Valid source payments could fail to load.

### Fix
The loader prepares a payment constraint that includes `BANK_TRANSFER`. This is a schema/constraint change performed by the loader and must be confirmed against the live database.

### Verification
The supplied project context says the payment data loaded successfully. Exact live constraint state is **To be verified**.

### Lesson
Constraints must reflect the accepted source domain.

## Refund and Payment Status Normalization

### Problem
Source statuses included `SUCCESS`, `PROCESSED`, `COMPLETED`, `PENDING`, and `FAILED`.

### Why it happened
Different systems can use different labels for the same business state.

### Impact
Direct insertion could violate constraints or split one business state into multiple labels.

### Fix
The loader maps `SUCCESS` and `PROCESSED` to `COMPLETED`, and preserves `COMPLETED`, `PENDING`, and `FAILED`.

### Verification
The mapping is visible in the remaining loader. Final live row counts are recorded in the validation document.

### Lesson
Normalization creates a consistent vocabulary for downstream analysis.

## Expense Category Mapping

### Problem
The source expense field is `category`, while the normalized target uses `expense_category`.

### Why it happened
Source and normalized schemas use different names.

### Impact
A positional or guessed insert could put values in the wrong column.

### Fix
The loader explicitly maps the source category value to the target expense category field.

### Verification
The mapping is recorded in the loader. Loaded expense count is supplied as 180.

### Lesson
Explicit column lists protect against schema-order mistakes.

## Login Event `logout_time`

### Problem
The source login file includes `logout_time`, but the normalized table does not currently include it.

### Why it happened
The normalized schema stores a smaller representation of the source event.

### Impact
That source field cannot be preserved in the current target table.

### Fix
The loader must intentionally omit or otherwise handle the field. Exact current loader behavior is **To be verified**.

### Verification
The source columns are known; target persistence of `logout_time` is **To be verified**.

### Lesson
A source-to-target mapping should document fields that are intentionally dropped.

## `updated_at` Versus `last_updated`

### Problem
An inventory metrics query referenced `inventory.updated_at`, but the repository schema uses `inventory.last_updated`.

### Why it happened
The source CSV uses `updated_at`, while the normalized database schema uses `last_updated`.

### Impact
PostgreSQL returned a missing-column error.

### Fix
SQL was aligned to the actual database column: `last_updated`.

### Verification
The schema definition contains `last_updated`. A live database check should still be performed before running future SQL.

### Lesson
Always inspect the target schema instead of copying source-column names into SQL.

## Inventory Validation CAST Error

### Problem
A validation message was incorrectly cast to `INTEGER`.

### Why it happened
A text error message was used as though it were a numeric validation gate.

### Impact
PostgreSQL returned error `22P02`, invalid input syntax for integer.

### Fix
The validation gate should be Boolean: true when no invalid balances exist and false otherwise.

### Verification
The invalid cast was identified from the PostgreSQL error. The corrected query must be tested separately.

### Lesson
Error messages and control values have different data types.

## PostgreSQL Transaction Error `25P02`

### Problem
After a statement failed inside a transaction, later statements reported that the current transaction was aborted.

### Why it happened
PostgreSQL marks the transaction failed until it is ended.

### Impact
Even valid follow-up queries could fail.

### Fix
Run `ROLLBACK;`, then execute the next query in a clean transaction.

### Verification
The project context records that rollback restored the ability to continue querying.

### Lesson
A transaction is not usable after an unhandled statement error until rollback or commit ends it.

## Interview Takeaway

- Data quality includes duplicates, domain mismatches, relationships, and schema differences.
- Preserve raw data and make transformations explicit.
- Use database errors as diagnostic evidence.
- Never hide a quality problem by silently converting it into a valid-looking value.
