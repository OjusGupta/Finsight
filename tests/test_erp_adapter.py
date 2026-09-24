from __future__ import annotations

import unittest
from datetime import datetime
from decimal import Decimal

from finops.erp_adapter import build_finance_lines_from_rows


class ErpAdapterTests(unittest.TestCase):
    def sale_row(self, **overrides):
        row = {
            "company_id": 1,
            "store_id": 2,
            "customer_id": 10,
            "sale_id": 100,
            "sale_item_id": 1001,
            "product_id": 200,
            "invoice_number": "INV-100",
            "sale_date": datetime(2026, 9, 24, 10, 30),
            "quantity": 2,
            "unit_price": Decimal("65.00"),
            "discount_amount": Decimal("4.50"),
            "tax_amount": Decimal("0.00"),
            "line_total": Decimal("125.50"),
            "sale_status": "COMPLETED",
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
            "return_date": datetime(2026, 9, 25, 10, 30),
            "refund_amount": Decimal("25.25"),
            "return_status": "COMPLETED",
        }
        row.update(overrides)
        return row

    def test_normal_sale_line_and_traceability(self):
        result = build_finance_lines_from_rows([self.sale_row()], [], {})
        self.assertEqual(len(result.lines), 1)
        line = result.lines[0]
        self.assertEqual(line.invoice_no, "INV-100")
        self.assertEqual(line.line_no, "1001")
        self.assertEqual(line.doc_type, "sale")
        self.assertEqual(line.line_total, Decimal("125.50"))
        self.assertEqual(line.metadata["company_id"], 1)
        self.assertEqual(line.metadata["store_id"], 2)
        self.assertEqual(line.metadata["customer_id"], 10)
        self.assertEqual(line.metadata["sale_id"], 100)
        self.assertEqual(line.metadata["sale_item_id"], 1001)
        self.assertEqual(line.metadata["product_id"], 200)
        self.assertEqual(line.metadata["source_table"], "sale_items")
        self.assertEqual(line.metadata["source_id"], 1001)

    def test_return_line_uses_negative_amount_and_namespaced_identity(self):
        result = build_finance_lines_from_rows([], [self.return_row()], {})
        self.assertEqual(len(result.lines), 1)
        line = result.lines[0]
        self.assertEqual(line.invoice_no, "sales_return:500")
        self.assertEqual(line.line_no, "501")
        self.assertEqual(line.doc_type, "sales_return")
        self.assertEqual(line.line_total, Decimal("-25.25"))
        self.assertEqual(line.metadata["return_id"], 500)
        self.assertEqual(line.metadata["return_item_id"], 501)
        self.assertEqual(line.metadata["sale_item_id"], 1001)

    def test_customer_id_is_preserved_without_inventing_customer_code(self):
        result = build_finance_lines_from_rows([self.sale_row()], [], {})
        line = result.lines[0]
        self.assertIsNone(line.customer_code)
        self.assertEqual(line.metadata["customer_id"], 10)
        self.assertIn("customer_code", line.metadata["missing_financial_fields"])

    def test_missing_sale_item_reference_is_rejected(self):
        result = build_finance_lines_from_rows(
            [], [self.return_row(sale_item_id=None, matched_sale_id=None)], {}
        )
        self.assertEqual(result.lines, ())
        self.assertEqual(result.report["normalized_return_lines"], 0)
        self.assertEqual(result.report["rejected_records"][0]["reason"], "missing_sale_item_reference")

    def test_mismatched_sale_item_reference_is_rejected(self):
        result = build_finance_lines_from_rows(
            [], [self.return_row(matched_sale_id=999)], {}
        )
        self.assertEqual(result.lines, ())
        self.assertEqual(result.report["rejected_records"][0]["reason"], "return_sale_item_mismatch")

    def test_decimal_values_and_tax_are_restored(self):
        result = build_finance_lines_from_rows([self.sale_row()], [], {})
        line = result.lines[0]
        self.assertIsInstance(line.line_total, Decimal)
        self.assertEqual(line.taxable_value, Decimal("125.50"))
        self.assertEqual(line.gst_amount, Decimal("0.00"))
        self.assertEqual(result.report["missing_financial_fields"]["customer_code"], 1)
        self.assertEqual(result.report["missing_financial_fields"]["taxable_value"], 0)
        self.assertEqual(result.report["missing_financial_fields"]["gst_amount"], 0)

    def test_report_counts_and_customer_coverage(self):
        result = build_finance_lines_from_rows(
            [
                self.sale_row(customer_id=10),
                self.sale_row(
                    sale_id=101,
                    sale_item_id=1002,
                    invoice_number="INV-101",
                    customer_id=None,
                ),
            ],
            [self.return_row(customer_id=10)],
        )
        self.assertEqual(result.report["sales_read"], 2)
        self.assertEqual(result.report["sale_items_read"], 2)
        self.assertEqual(result.report["returns_read"], 1)
        self.assertEqual(result.report["return_items_read"], 1)
        self.assertEqual(result.report["normalized_sale_lines"], 2)
        self.assertEqual(result.report["normalized_return_lines"], 1)
        self.assertEqual(result.report["customer_id_coverage"], {
            "lines_total": 3,
            "present": 2,
            "missing": 1,
        })


if __name__ == "__main__":
    unittest.main()
