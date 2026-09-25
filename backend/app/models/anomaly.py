from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric

from backend.app.database.connection import Base


class Anomaly(Base):
    __tablename__ = "anomalies"

    anomaly_id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, nullable=True)
    product_id = Column(Integer, nullable=True)
    sale_id = Column(Integer, nullable=True)
    anomaly_type = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    detected_value = Column(Numeric(14, 2), nullable=True)
    expected_value = Column(Numeric(14, 2), nullable=True)
    detection_method = Column(String(50), nullable=False)
    status = Column(String(30), nullable=False)
    detected_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
