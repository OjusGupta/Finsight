from __future__ import annotations

import unittest

from finops.finance_analytics import build_finance_anomaly_candidates


class FinanceAnalyticsTests(unittest.TestCase):
    def test_blocked_finance_line_becomes_traceable_anomaly(self):
        candidates = build_finance_anomaly_candidates(
            [{
                "run_id": 1,
                "finance_line_id": 9,
                "invoice_no": "sales_return:5",
                "line_no": "7",
                "finance_state": "FINANCE_FIELDS_INCOMPLETE",
                "rejection_reason": "missing taxable_value/gst_amount",
                "line_total": -25,
                "company_id": 1,
                "store_id": 2,
                "customer_id": 10,
                "product_id": 20,
                "sale_id": 30,
                "sale_item_id": 40,
                "return_id": 50,
                "return_item_id": 60,
            }],
            [],
        )
        self.assertEqual(len(candidates), 1)
        candidate = candidates[0]
        self.assertEqual(candidate["anomaly_type"], "FINANCE_FIELDS_INCOMPLETE")
        self.assertIn("finance_line_id=9", candidate["description"])
        self.assertIn("return_id=50", candidate["description"])
        self.assertEqual(candidate["sale_id"], 30)

    def test_posting_failure_and_retry_rules(self):
        candidates = build_finance_anomaly_candidates(
            [],
            [
                {
                    "run_id": 1,
                    "posting_id": 10,
                    "invoice_no": "INV-1",
                    "idempotency_key": "INV-1",
                    "posting_status": "PERMANENT_FAILURE",
                    "attempt_count": 3,
                    "last_http_status": 422,
                    "timeout_observed": False,
                    "last_error": "invalid",
                },
                {
                    "run_id": 1,
                    "posting_id": 11,
                    "invoice_no": "INV-2",
                    "idempotency_key": "INV-2",
                    "posting_status": "POSTED",
                    "attempt_count": 2,
                    "last_http_status": 201,
                    "timeout_observed": False,
                    "last_error": None,
                },
            ],
        )
        self.assertEqual(
            [candidate["anomaly_type"] for candidate in candidates],
            ["ACCOUNTING_POSTING_FAILURE", "ACCOUNTING_POSTING_RETRY"],
        )

    def test_successful_posting_has_no_anomaly(self):
        candidates = build_finance_anomaly_candidates(
            [],
            [{
                "run_id": 1,
                "posting_id": 10,
                "invoice_no": "INV-1",
                "idempotency_key": "INV-1",
                "posting_status": "POSTED",
                "attempt_count": 1,
                "last_http_status": 201,
                "timeout_observed": False,
                "last_error": None,
            }],
        )
        self.assertEqual(candidates, [])


if __name__ == "__main__":
    unittest.main()
