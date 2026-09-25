from sqlalchemy import Column, Integer, Date, DateTime, Numeric

from backend.app.database.connection import Base


class DailyStoreMetric(Base):
    __tablename__ = "daily_store_metrics"

    metric_id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, nullable=False)
    metric_date = Column(Date, nullable=False)
    total_sales = Column(Numeric(14, 2), nullable=False)
    total_orders = Column(Integer, nullable=False)
    total_returns = Column(Numeric(14, 2), nullable=False)
    total_expenses = Column(Numeric(14, 2), nullable=False)
    net_sales = Column(Numeric(14, 2), nullable=False)
    created_at = Column(DateTime, nullable=True)