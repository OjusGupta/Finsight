from sqlalchemy.orm import Session

from backend.app.models.inventory_metric import InventoryMetric


def get_all_inventory_metrics(db: Session):
    return (
        db.query(InventoryMetric)
        .order_by(
            InventoryMetric.metric_date.desc(),
            InventoryMetric.inventory_id
        )
        .all()
    )