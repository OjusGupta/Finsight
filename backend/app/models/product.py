from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime

from backend.app.database.connection import Base


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, nullable=False)
    product_name = Column(String(200), nullable=False)
    sku = Column(String(100), nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    cost_price = Column(Numeric(12, 2), nullable=False)
    is_active = Column(Boolean, nullable=True)
    created_at = Column(DateTime, nullable=True)
