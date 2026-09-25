from sqlalchemy.orm import Session

from backend.app.models.sale import Sale


def get_all_sales(db: Session):
    return db.query(Sale).order_by(Sale.sale_id).all()
