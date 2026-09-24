from __future__ import annotations

import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock

from finops.accounting_client import AccountingResponse
from finops.mock_accounting import MockAccountingClient
from finops.models import AccountingTimeout, InvoiceDocument, NormalizedLine
from finops.phase4 import _reconciled_documents
from finops.posting import PostingEngine
from finops.postgres_persistence import PostgresPersistence
from finops.reconciliation import reconcile_normalized_lines


class MemoryState:
    def __init__(self):
        self.posted = set()
        self.attempts = []
        self.final = []

    def contains(self, invoice_no):
        return invoice_no in self.posted

    def record(self, invoice_no, second, third=None, **result):
        if isinstance(second, int):
            self.attempts.append((invoice_no, second, result))
        else:
            self.posted.add(invoice_no)
            self.final.append((invoice_no, second, third))


def document(invoice_no="INV-PHASE4", doc_type="sale"):
    return InvoiceDocument(
        invoice_no=invoice_no,
        doc_type=doc_type,
        customer_code=None,
        lines=(
            NormalizedLine(
                invoice_no=invoice_no,
                line_no="1",
                doc_type=doc_type,
                transaction_date=date(2026, 9, 24),
                customer_code=None,
                line_total=Decimal("100.00") if doc_type == "sale" else Decimal("-25.00"),
                taxable_value=Decimal("95.00") if doc_type == "sale" else None,
                gst_amount=Decimal("5.00") if doc_type == "sale" else None,
                raw={},
                metadata={"sale_id": 10},
            ),
        ),
    )


class Phase4PostingTests(unittest.TestCase):
    def run_posting(self, client, invoice="INV-PHASE4"):
        state = MemoryState()
        engine = PostingEngine(client, state, state)
        report = engine.post_documents([document(invoice)])
        return report, state

    def test_mock_201_posts_once(self):
        report, state = self.run_posting(MockAccountingClient())
        self.assertEqual(report["invoices_posted"], 1)
        self.assertEqual(len(state.final), 1)

    def test_mock_409_is_idempotent_success(self):
        client = MockAccountingClient(lambda attempt, _: AccountingResponse(409, "existing"))
        report, state = self.run_posting(client)
        self.assertEqual(report["invoices_posted"], 1)
        self.assertEqual(len(client.calls), 1)
        self.assertEqual(state.final[0][2], "already_posted")

    def test_422_does_not_retry(self):
        client = MockAccountingClient(lambda attempt, _: AccountingResponse(422))
        report, _ = self.run_posting(client)
        self.assertEqual(report["invoices_failed"], 1)
        self.assertEqual(len(client.calls), 1)

    def test_timeout_then_success_reuses_key(self):
        client = MockAccountingClient(
            lambda attempt, _: AccountingTimeout() if attempt == 1 else AccountingResponse(201, "doc")
        )
        report, _ = self.run_posting(client)
        self.assertEqual(report["invoices_posted"], 1)
        self.assertEqual([key for key, _ in client.calls], ["INV-PHASE4", "INV-PHASE4"])

    def test_failure_after_three_attempts(self):
        client = MockAccountingClient(lambda attempt, _: AccountingResponse(503))
        report, _ = self.run_posting(client)
        self.assertEqual(report["invoices_failed"], 1)
        self.assertEqual(len(client.calls), 3)

    def test_rerun_skips_already_posted(self):
        client = MockAccountingClient()
        state = MemoryState()
        engine = PostingEngine(client, state, state)
        engine.post_documents([document()])
        report = engine.post_documents([document()])
        self.assertEqual(report["invoices_skipped_already_posted"], 1)
        self.assertEqual(len(client.calls), 1)

    def test_blocked_return_is_not_posted(self):
        client = MockAccountingClient()
        state = MemoryState()
        engine = PostingEngine(client, state, state)
        blocked = document("sales_return:5", "sales_return")
        reconciliation = reconcile_normalized_lines(blocked.lines)
        eligible = _reconciled_documents(blocked.lines, reconciliation)
        report = engine.post_documents(eligible)
        self.assertEqual(report["invoices_seen"], 0)
        self.assertEqual(len(client.calls), 0)

    def test_persistence_store_emits_run_line_and_posting_operations(self):
        connection = MagicMock()
        cursor = MagicMock()
        cursor.fetchone.return_value = (42,)
        connection.cursor.return_value = cursor
        store = PostgresPersistence(connection)
        run_id = store.create_run({}, {
            "lines_read": 1,
            "structurally_valid_lines": 1,
            "invalid_lines": 0,
            "duplicate_lines_skipped": 0,
            "invoices_processed": 1,
            "invoices_reconciled": 1,
            "invoices_blocked_from_posting": 0,
            "amount_reconciled": "100.00",
            "invoice_states": [{
                "invoice_no": "INV-PHASE4",
                "state": "RECONCILED",
                "posting_allowed": True,
                "amount": "100.00",
            }],
        })
        self.assertEqual(run_id, 42)
        line = NormalizedLine(
            invoice_no="INV-PHASE4",
            line_no="1",
            doc_type="sale",
            transaction_date=date(2026, 9, 24),
            customer_code=None,
            line_total=Decimal("100.00"),
            taxable_value=Decimal("95.00"),
            gst_amount=Decimal("5.00"),
            raw={},
            metadata={"source_table": "sale_items", "source_id": 10},
        )
        store.persist_lines((line,), {
            "invoice_states": [{
                "invoice_no": "INV-PHASE4",
                "state": "RECONCILED",
                "posting_allowed": True,
            }],
        })
        store.record("INV-PHASE4", 1, result="success", status_code=201)
        store.record("INV-PHASE4", "doc-1", "success")
        statements = [str(call.args[0]) for call in cursor.execute.call_args_list]
        self.assertTrue(any("finance_reconciliation_runs" in statement for statement in statements))
        self.assertTrue(any("finance_reconciliation_lines" in statement for statement in statements))
        self.assertTrue(any("accounting_postings" in statement for statement in statements))


if __name__ == "__main__":
    unittest.main()
