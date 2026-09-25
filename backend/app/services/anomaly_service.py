from sqlalchemy.orm import Session

from backend.app.models.anomaly import Anomaly


def get_all_anomalies(db: Session):
    return db.query(Anomaly).order_by(Anomaly.anomaly_id).all()