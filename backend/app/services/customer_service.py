from sqlalchemy.orm import Session

from backend.app.models.customer import Customer


def get_all_customers(db: Session):
    return db.query(Customer).order_by(Customer.customer_id).all()
