from sqlalchemy.orm import Session

from backend.app.models.product import Product


def get_all_products(db: Session):
    return db.query(Product).order_by(Product.product_id).all()
