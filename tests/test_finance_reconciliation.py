from __future__ import annotations

import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from finops.accounting_client import AccountingResponse
from finops.deduplication import deduplicate_lines
from finops.journal import PostingJournal
from finops.ledger import PostedLedger
from finops.models import AccountingTimeout
from finops.money import format_money, parse_money
from finops.parsing import parse_business_date
from finops.pipeline import REPORT_KEYS
from finops.posting import PostingEngine
from finops.validation import validate_line


class FakeClient:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = []

    def post(self, document, idempotency_key):
        self.calls.append((document, idempotency_key))
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


def line(**overrides):
    result = {
        "invoice_no": "INV-1",
        "line_no": "1",
        "doc_type": "sale",
        "transaction_date": "24-09-2026",
        "customer_code": " c001 ",
        "line_total": "100.00",
        "taxable_value": "95.00",
        "gst_amount": "5.00",
    }
    result.update(overrides)
    return result


class FinanceReconciliationTests(unittest.TestCase):
    def test_money_formats_and_rejection(self):
        self.assertEqual(parse_money("845.75"), Decimal("845.75"))
        self.assertEqual(parse_money("1,20,000.00"), Decimal("120000.00"))
        self.assertEqual(parse_money("Rs. 12,345.00"), Decimal("12345.00"))
        self.assertEqual(parse_money("(9,675.01)"), Decimal("-9675.01"))
        self.assertEqual(parse_money("9,675.01-"), Decimal("-9675.01"))
        self.assertEqual(format_money(Decimal("1.005")), "1.01")
        with self.assertRaisesRegex(ValueError, "bad_amount"):
            parse_money("12,34.56")

    def test_date_formats_and_rejection(self):
        expected = date(2026, 9, 24)
        self.assertEqual(parse_business_date("24-09-2026"), expected)
        self.assertEqual(parse_business_date("24/09/2026"), expected)
        self.assertEqual(parse_business_date("2026-09-24"), expected)
        with self.assertRaisesRegex(ValueError, "bad_date"):
            parse_business_date("31/02/2026")
        with self.assertRaisesRegex(ValueError, "bad_date"):
            parse_business_date("9/24/2026")

    def test_sign_validation(self):
        self.assertFalse(hasattr(validate_line(line(), date(2026, 9, 24)), "reason"))
        rejected_sale = validate_line(line(line_total="(1.00)"), date(2026, 9, 24))
        self.assertEqual(rejected_sale.reason, "sign_mismatch")
        returned = validate_line(
            line(doc_type="sales_return", line_total="(10.00)", taxable_value="(9.50)", gst_amount="(0.50)"),
            date(2026, 9, 24),
        )
        self.assertEqual(returned.doc_type, "sales_return")
        rejected_return = validate_line(
            line(doc_type="sales_return", line_total="10.00"), date(2026, 9, 24)
        )
        self.assertEqual(rejected_return.reason, "sign_mismatch")

    def test_future_date_is_rejected(self):
        rejected = validate_line(line(transaction_date="25-09-2026"), date(2026, 9, 24))
        self.assertEqual(rejected.reason, "future_date")

    def test_duplicate_lines(self):
        result = deduplicate_lines([line(), line()])
        self.assertEqual(len(result.rows), 1)
        self.assertEqual(result.duplicate_lines_skipped, 1)
        self.assertFalse(result.rejects)

        conflict = deduplicate_lines([line(line_total="100.00"), line(line_total="101.00")])
        self.assertEqual(len(conflict.rejects), 2)
        self.assertEqual(conflict.rejects[0].reason, "conflicting_duplicate")

    def test_customer_resolution_and_unknown_customer(self):
        with tempfile.TemporaryDirectory() as directory:
            client = FakeClient([AccountingResponse(201, "doc-1")])
            engine = PostingEngine(
                client,
                PostedLedger(Path(directory) / "ledger.json"),
                PostingJournal(Path(directory) / "journal.json"),
            )
            report = engine.run([line(customer_code=" unknown ")], {"C001": "C001"}, date(2026, 9, 24))
            self.assertEqual(report["invoices_unknown_customer"], 1)
            self.assertEqual(report["invoices_posted"], 1)

    def test_reconciliation_tolerance_and_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            client = FakeClient([AccountingResponse(201, "doc-1")])
            engine = PostingEngine(
                client,
                PostedLedger(Path(directory) / "ledger.json"),
                PostingJournal(Path(directory) / "journal.json"),
            )
            within = engine.run(
                [line(line_total="100.04", taxable_value="95.00", gst_amount="5.00")],
                {"C001": "C001"},
                date(2026, 9, 24),
            )
            self.assertEqual(within["invoices_posted"], 1)

            mismatch = engine.run(
                [line(invoice_no="INV-2", line_total="100.06", taxable_value="95.00", gst_amount="5.00")],
                {"C001": "C001"},
                date(2026, 9, 24),
            )
            self.assertEqual(mismatch["invoices_rejected"], 1)
            self.assertEqual(mismatch["rejected_invoices"][0]["reason"], "total_mismatch")

    def test_partial_invoice_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            client = FakeClient([])
            engine = PostingEngine(
                client,
                PostedLedger(Path(directory) / "ledger.json"),
                PostingJournal(Path(directory) / "journal.json"),
            )
            report = engine.run(
                [line(), line(line_no="2", line_total="-2.00")],
                {"C001": "C001"},
                date(2026, 9, 24),
            )
            self.assertEqual(report["invoices_rejected"], 1)
            self.assertEqual(report["invoices_posted"], 0)
            self.assertEqual(report["rejected_invoices"][0]["reason"], "incomplete_invoice")

    def test_api_statuses_and_retry(self):
        cases = [
            ([AccountingResponse(201, "doc")], 1, 1, 0),
            ([AccountingResponse(409, "existing")], 1, 1, 0),
            ([AccountingResponse(422)], 1, 0, 1),
            ([AccountingResponse(500), AccountingResponse(503), AccountingResponse(201, "doc")], 3, 1, 0),
            ([AccountingResponse(500)] * 3, 3, 0, 1),
        ]
        for outcomes, calls, posted, failed in cases:
            with self.subTest(outcomes=outcomes):
                with tempfile.TemporaryDirectory() as directory:
                    fake = FakeClient(outcomes)
                    engine = PostingEngine(
                        fake,
                        PostedLedger(Path(directory) / "ledger.json"),
                        PostingJournal(Path(directory) / "journal.json"),
                    )
                    report = engine.run([line()], {"C001": "C001"}, date(2026, 9, 24))
                    self.assertEqual(len(fake.calls), calls)
                    self.assertEqual(report["invoices_posted"], posted)
                    self.assertEqual(report["invoices_failed"], failed)
                    self.assertTrue(all(call[1] == "INV-1" for call in fake.calls))

    def test_timeout_retries_with_same_key(self):
        with tempfile.TemporaryDirectory() as directory:
            fake = FakeClient([AccountingTimeout(), AccountingResponse(201, "doc")])
            engine = PostingEngine(
                fake,
                PostedLedger(Path(directory) / "ledger.json"),
                PostingJournal(Path(directory) / "journal.json"),
            )
            report = engine.run([line()], {"C001": "C001"}, date(2026, 9, 24))
            self.assertEqual(report["invoices_posted"], 1)
            self.assertEqual([call[1] for call in fake.calls], ["INV-1", "INV-1"])

    def test_ledger_skips_rerun_and_journal_is_written(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger_path = Path(directory) / "ledger.json"
            journal_path = Path(directory) / "journal.json"
            fake = FakeClient([AccountingResponse(201, "doc")])
            first = PostingEngine(fake, PostedLedger(ledger_path), PostingJournal(journal_path))
            first.run([line()], {"C001": "C001"}, date(2026, 9, 24))
            second = PostingEngine(fake, PostedLedger(ledger_path), PostingJournal(journal_path))
            report = second.run([line()], {"C001": "C001"}, date(2026, 9, 24))
            self.assertEqual(report["invoices_skipped_already_posted"], 1)
            self.assertEqual(len(fake.calls), 1)
            self.assertTrue(journal_path.exists())

    def test_report_schema_and_identities(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = PostingEngine(
                FakeClient([AccountingResponse(201, "doc")]),
                PostedLedger(Path(directory) / "ledger.json"),
                PostingJournal(Path(directory) / "journal.json"),
            )
            report = engine.run([line(), line()], {"C001": "C001"}, date(2026, 9, 24))
            self.assertEqual(set(report), REPORT_KEYS)
            self.assertEqual(report["amount_posted"], "100.00")
            self.assertEqual(
                report["lines_read"],
                report["duplicate_lines_skipped"] + report["lines_valid"] + report["lines_rejected"],
            )
            self.assertEqual(
                report["invoices_seen"],
                report["invoices_posted"]
                + report["invoices_skipped_already_posted"]
                + report["invoices_failed"]
                + report["invoices_rejected"],
            )


if __name__ == "__main__":
    unittest.main()
