# Finance Reconciliation Policy
## Definitions
- **Reconciliation Engine**: The system that matches sales records to accounting postings and payments.
- **FINANCE_FIELDS_INCOMPLETE**: This error means an invoice is blocked because mandatory fields (like customer billing info or tax codes) are missing.
- **BLOCKED**: The document is withheld from posting to the general ledger due to discrepancies.

## Action Plan for Blocked Invoices
1. If blocked for FINANCE_FIELDS_INCOMPLETE, the finance manager must update the missing fields in the ERP.
2. If blocked for value mismatches (e.g., payment does not match invoice total), the transaction must be flagged for manual review.
3. No blocked document can be force-posted without administrator approval.
