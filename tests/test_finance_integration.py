from __future__ import annotations

import unittest
from datetime import date
from decimal import Decimal

from finops.erp_adapter import build_finance_lines_from_rows
from finops.integration import reconcile_adapter_result
from finops.models import NormalizedLine
from finops.reconciliation import reconcile_normalized_lines


class FinanceIntegrationTests(unittest.TestCase):
    def sale_row(self, **overrides):
        row = {
            "company_id": 1,
            "store_id": 2,
            "customer_id": 10,
            "sale_id": 100,
            "sale_item_id": 1001,
            "product_id": 200,
            "invoice_number": "INV-100",
            "sale_date": date(2026, 9, 24),
            "quantity": 2,
            "unit_price": Decimal("65.00"),
            "discount_amount": Decimal("4.50"),
            "tax_amount": Decimal("0.00"),
            "line_total": Decimal("125.50"),
        }
        row.update(overrides)
        return row

    def return_row(self, **overrides):
        row = {
            "company_id": 1,
            "store_id": 2,
            "customer_id": 10,
            "sale_id": 100,
            "return_id": 500,
            "return_item_id": 501,
            "sale_item_id": 1001,
            "matched_sale_id": 100,
            "product_id": 200,
            "return_date": date(2026, 9, 25),
            "refund_amount": Decimal("25.25"),
        }
        row.update(overrides)
        return row

    def test_adapter_output_enters_reconciliation_without_posting(self):
        adapter_result = build_finance_lines_from_rows(
            [self.sale_row()], [self.return_row()]
        )
        integrated = reconcile_adapter_result(adapter_result)
        reconciliation = integrated["reconciliation"]

        self.assertEqual(reconciliation["lines_read"], 2)
        self.assertEqual(reconciliation["invoices_processed"], 2)
        self.assertEqual(reconciliation["invoices_reconciled"], 1)
        self.assertEqual(reconciliation["invoices_eligible_for_complete_reconciliation"], 1)
        self.assertEqual(reconciliation["invoices_blocked_from_posting"], 1)
        self.assertEqual(
            reconciliation["state_counts"],
            {"FINANCE_FIELDS_INCOMPLETE": 1, "RECONCILED": 1},
        )
        self.assertEqual(reconciliation["missing_financial_fields"]["gst_amount"], 1)

    def test_traceability_survives_adapter_to_engine_boundary(self):
        adapter_result = build_finance_lines_from_rows(
            [self.sale_row()], [self.return_row()]
        )
        self.assertEqual(adapter_result.lines[0].metadata["sale_id"], 100)
        self.assertEqual(adapter_result.lines[0].metadata["sale_item_id"], 1001)
        self.assertEqual(adapter_result.lines[1].metadata["return_id"], 500)
        self.assertEqual(adapter_result.lines[1].metadata["return_item_id"], 501)
        self.assertEqual(adapter_result.lines[1].line_total, Decimal("-25.25"))
        integrated = reconcile_adapter_result(adapter_result)
        states = {item["invoice_no"]: item for item in integrated["reconciliation"]["invoice_states"]}
        self.assertEqual(states["INV-100"]["state"], "RECONCILED")
        self.assertEqual(states["sales_return:500"]["state"], "FINANCE_FIELDS_INCOMPLETE")

    def test_complete_line_can_reconcile_without_posting(self):
        line = NormalizedLine(
            invoice_no="INV-COMPLETE",
            line_no="1",
            doc_type="sale",
            transaction_date=date(2026, 9, 24),
            customer_code=None,
            line_total=Decimal("100.00"),
            taxable_value=Decimal("95.00"),
            gst_amount=Decimal("5.00"),
            raw={},
            metadata={"customer_id": 10},
        )
        report = reconcile_normalized_lines([line])
        self.assertEqual(report["state_counts"], {"RECONCILED": 1})
        self.assertEqual(report["invoices_eligible_for_complete_reconciliation"], 1)
        self.assertEqual(report["invoices_blocked_from_posting"], 0)

    def test_conflicting_normalized_duplicates_are_blocked(self):
        first = NormalizedLine(
            invoice_no="INV-DUP",
            line_no="1",
            doc_type="sale",
            transaction_date=date(2026, 9, 24),
            customer_code=None,
            line_total=Decimal("100.00"),
            taxable_value=None,
            gst_amount=None,
            raw={"value": 1},
        )
        second = NormalizedLine(
            invoice_no="INV-DUP",
            line_no="1",
            doc_type="sale",
            transaction_date=date(2026, 9, 24),
            customer_code=None,
            line_total=Decimal("101.00"),
            taxable_value=None,
            gst_amount=None,
            raw={"value": 2},
        )
        report = reconcile_normalized_lines([first, second])
        self.assertEqual(report["conflicting_duplicate_invoices"], 1)
        self.assertEqual(report["state_counts"], {"CONFLICTING_DUPLICATE": 1})
        self.assertEqual(report["invoices_blocked_from_posting"], 1)


if __name__ == "__main__":
    unittest.main()
