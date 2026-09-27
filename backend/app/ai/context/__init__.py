"""AI context package exports.
Provides convenient functions to build structured finance context for LLMs.
"""

from .service import (
    build_latest_finance_context,
    build_reconciliation_context,
    build_blocked_documents_context,
    build_posting_context,
    build_anomaly_context,
)
