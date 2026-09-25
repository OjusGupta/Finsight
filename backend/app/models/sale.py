from sqlalchemy import Column, Integer, String, DateTime, Numeric

from backend.app.database.connection import Base


class Sale(Base):
    __tablename__ = "sales"

    sale_id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, nullable=False)
    customer_id = Column(Integer, nullable=True)
    user_id = Column(Integer, nullable=True)
    invoice_number = Column(String(100), nullable=False)
    sale_date = Column(DateTime, nullable=True)
    subtotal = Column(Numeric(12, 2), nullable=False)
    discount_amount = Column(Numeric(12, 2), nullable=False)
    tax_amount = Column(Numeric(12, 2), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String(30), nullable=False)
