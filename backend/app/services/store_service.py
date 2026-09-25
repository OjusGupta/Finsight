from sqlalchemy.orm import Session

from backend.app.models.store import Store


def get_all_stores(db: Session):
    return db.query(Store).order_by(Store.store_id).all()