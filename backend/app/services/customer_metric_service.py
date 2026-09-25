from sqlalchemy.orm import Session

from backend.app.models.customer_metric import CustomerMetric


def get_all_customer_metrics(db: Session):
    return (
        db.query(CustomerMetric)
        .order_by(
            CustomerMetric.metric_date.desc(),
            CustomerMetric.customer_id
        )
        .all()
    )