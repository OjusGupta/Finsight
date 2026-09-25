from sqlalchemy.orm import Session

from backend.app.models.inventory import Inventory


def get_all_inventory(db: Session):
    return db.query(Inventory).order_by(Inventory.inventory_id).all()
