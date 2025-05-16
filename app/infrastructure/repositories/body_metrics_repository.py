from sqlalchemy.orm import Session
import uuid
from typing import Optional, Dict, Any
from app.infrastructure.db.models import Anthropometries

class BodyMetricsRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_anthropometry(self, patient_id: int, data: Dict[str, Any]) -> uuid.UUID:
        record = Anthropometries(
            id=uuid.uuid4(),
            patient_id=patient_id,
            **data
        )
        self.session.add(record)
        self.session.commit()
        return record.id

    def get_latest_metrics(self, patient_id: int) -> Optional[Dict[str, Any]]:
        record = (
            self.session.query(Anthropometries)
            .filter_by(patient_id=patient_id)
            .order_by(Anthropometries.measured_at.desc())
            .first()
        )
        return record.__dict__ if record else None
