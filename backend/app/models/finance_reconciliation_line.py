from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.connection import Base


class FinanceReconciliationLine(Base):
    __tablename__ = "finance_reconciliation_lines"

    finance_line_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    run_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    source_table: Mapped[str] = mapped_column(String(50), nullable=False)
    source_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    company_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    store_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    customer_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    product_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    sale_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sale_item_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    return_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    return_item_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    invoice_no: Mapped[str] = mapped_column(String(100), nullable=False)
    line_no: Mapped[str] = mapped_column(String(100), nullable=False)

    doc_type: Mapped[str] = mapped_column(String(30), nullable=False)

    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)

    customer_code: Mapped[str | None] = mapped_column(String(100), nullable=True)

    line_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    taxable_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    gst_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)

    finance_state: Mapped[str] = mapped_column(String(50), nullable=False)
    rejection_reason: Mapped[str | None] = mapped_column(String(100), nullable=True)

    posting_allowed: Mapped[bool] = mapped_column(Boolean, nullable=False)

    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
