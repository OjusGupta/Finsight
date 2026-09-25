from sqlalchemy import Column, Integer, Date, DateTime, Numeric

from backend.app.database.connection import Base


class ProductPerformance(Base):
    __tablename__ = "product_performance"

    performance_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False)
    metric_date = Column(Date, nullable=False)
    units_sold = Column(Integer, nullable=False)
    revenue = Column(Numeric(14, 2), nullable=False)
    units_returned = Column(Integer, nullable=False)
    return_amount = Column(Numeric(14, 2), nullable=False)
    created_at = Column(DateTime, nullable=True)