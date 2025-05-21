import uuid
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session, joinedload

from app.domain.repositories.body_metrics_repository_interface import IBodyMetricsRepository
from app.infrastructure.db.models import Anthropometries
from app.services.metrics_recalculator import recompute_body_metrics


class BodyMetricsRepository(IBodyMetricsRepository):  # 👈 наследуем интерфейс
    def __init__(self, session: Session):
        self.session = session

    # ────────────────────────────────────────────────────────
    # helpers
    # ────────────────────────────────────────────────────────
    @staticmethod
    def _calc_metrics(height_cm: float, weight_kg: float) -> Dict[str, float]:
        """Простейшие формулы: BMI и BSA (Mosteller). Допишите свои, если нужно."""
        h_m = height_cm / 100
        bmi = weight_kg / (h_m ** 2) if h_m else None
        bsa = ((height_cm * weight_kg) / 3600) ** 0.5
        return {"bmi": bmi, "bsa": bsa}

    # ────────────────────────────────────────────────────────
    # public API
    # ────────────────────────────────────────────────────────

    def add_anthropometry(self, patient_id: int, data: Dict[str, Any]) -> uuid.UUID:
        anthropometry = Anthropometries(patient_id=patient_id, **data)
        self.session.add(anthropometry)
        self.session.flush()  # чтобы получить ID

        self.session.refresh(anthropometry, attribute_names=["patient"])  # ← .patient подгружается
        recompute_body_metrics(self.session, anthropometry)

        self.session.commit()
        return anthropometry.id

    def get_latest_metrics(
            self, patient_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Возвращаем словарь формата
        `{..., "bmi": ..., "bsa": ..., ...}`
        (поля из обеих таблиц).
        """
        record: Optional[Anthropometries] = (
            self.session.query(Anthropometries)
            .options(joinedload(Anthropometries.body_metrics))  # relationship зададим ниже
            .filter_by(patient_id=patient_id)
            .order_by(Anthropometries.measured_at.desc())
            .first()
        )
        if not record:
            return None

        # convert SQLAlchemy obj → dict, объединяем
        anth_dict = {
            k: v
            for k, v in record.__dict__.items()
            if not k.startswith("_")
        }
        if record.body_metrics:
            anth_dict.update(
                {
                    k: v
                    for k, v in record.body_metrics.__dict__.items()
                    if not k.startswith("_") and k != "id"
                }
            )
        return anth_dict
