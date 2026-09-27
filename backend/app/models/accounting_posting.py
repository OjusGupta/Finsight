from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.connection import Base


class AccountingPosting(Base):
    __tablename__ = "accounting_postings"

    posting_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    run_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    invoice_no: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    doc_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    idempotency_key: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    reconciliation_state: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    posting_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    attempt_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    external_document_id: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    last_http_status: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    last_result: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    timeout_observed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    attempt_history: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
    )

    first_attempt_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    last_attempt_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    posted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )