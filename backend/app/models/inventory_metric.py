from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric

from backend.app.database.connection import Base


class InventoryMetric(Base):
    __tablename__ = "inventory_metrics"

    metric_id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, nullable=False)
    metric_date = Column(Date, nullable=False)
    opening_quantity = Column(Integer, nullable=False)
    closing_quantity = Column(Integer, nullable=False)
    units_sold = Column(Integer, nullable=False)
    units_received = Column(Integer, nullable=False)
    units_returned = Column(Integer, nullable=False)
    stock_value = Column(Numeric(14, 2), nullable=False)
    reorder_level = Column(Integer, nullable=False)
    stock_status = Column(String(30), nullable=False)
    created_at = Column(DateTime, nullable=True)