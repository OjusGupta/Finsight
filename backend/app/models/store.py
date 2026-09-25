from sqlalchemy import Column, Integer, String, Text, DateTime

from backend.app.database.connection import Base


class Store(Base):
    __tablename__ = "stores"

    store_id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, nullable=False)
    store_name = Column(String(150), nullable=False)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)