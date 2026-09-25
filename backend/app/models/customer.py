from sqlalchemy import Column, Integer, String, DateTime

from backend.app.database.connection import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=True)
    phone = Column(String(30), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=True)