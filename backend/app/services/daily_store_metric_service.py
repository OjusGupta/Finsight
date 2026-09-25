from sqlalchemy.orm import Session

from backend.app.models.daily_store_metric import DailyStoreMetric


def get_all_daily_store_metrics(db: Session):
    return (
        db.query(DailyStoreMetric)
        .order_by(
            DailyStoreMetric.metric_date.desc(),
            DailyStoreMetric.store_id
        )
        .all()
    )