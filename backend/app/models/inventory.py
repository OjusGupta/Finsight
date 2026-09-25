from sqlalchemy import Column, Integer, DateTime

from backend.app.database.connection import Base


class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    reorder_level = Column(Integer, nullable=False)
    last_updated = Column(DateTime, nullable=True)