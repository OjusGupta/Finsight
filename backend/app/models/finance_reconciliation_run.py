from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.connection import Base


class FinanceReconciliationRun(Base):
    __tablename__ = "finance_reconciliation_runs"

    run_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    source_system: Mapped[str] = mapped_column(String(100), nullable=False)

    run_started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    run_completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    status: Mapped[str] = mapped_column(String(40), nullable=False)

    lines_read: Mapped[int] = mapped_column(Integer, nullable=False)
    lines_valid: Mapped[int] = mapped_column(Integer, nullable=False)
    lines_rejected: Mapped[int] = mapped_column(Integer, nullable=False)
    duplicate_lines_skipped: Mapped[int] = mapped_column(Integer, nullable=False)

    invoices_processed: Mapped[int] = mapped_column(Integer, nullable=False)
    invoices_reconciled: Mapped[int] = mapped_column(Integer, nullable=False)
    invoices_blocked: Mapped[int] = mapped_column(Integer, nullable=False)

    amount_reconciled: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    amount_blocked: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    summary_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
