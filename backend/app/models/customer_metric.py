from sqlalchemy import Column, Integer, Date, DateTime, Numeric

from backend.app.database.connection import Base


class CustomerMetric(Base):
    __tablename__ = "customer_metrics"

    metric_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False)
    metric_date = Column(Date, nullable=False)
    total_orders = Column(Integer, nullable=False)
    total_spent = Column(Numeric(14, 2), nullable=False)
    total_items_purchased = Column(Integer, nullable=False)
    total_returns = Column(Integer, nullable=False)
    total_refund_amount = Column(Numeric(14, 2), nullable=False)
    created_at = Column(DateTime, nullable=True)