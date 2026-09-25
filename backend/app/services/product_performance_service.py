from sqlalchemy.orm import Session

from backend.app.models.product_performance import ProductPerformance


def get_all_product_performance(db: Session):
    return (
        db.query(ProductPerformance)
        .order_by(
            ProductPerformance.metric_date.desc(),
            ProductPerformance.product_id
        )
        .all()
    )