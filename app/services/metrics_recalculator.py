from uuid import uuid4

from sqlalchemy.orm import Session

from app.formulas import bmi, bsa_mosteller, bmr_mifflin, Sex
from app.infrastructure.db.models import Anthropometries, BodyMetrics


def recompute_body_metrics(session: Session, anthropometry: Anthropometries):
    if not anthropometry.patient:
        raise ValueError("Patient must be eagerly loaded with anthropometry")

    age = (anthropometry.measured_at.date() - anthropometry.patient.birth_date).days // 365
    sex = Sex(anthropometry.patient.sex)

    bmi_val = bmi(anthropometry.weight_kg, anthropometry.height_cm)
    bsa_val = bsa_mosteller(anthropometry.weight_kg, anthropometry.height_cm)
    bmr_val = bmr_mifflin(anthropometry.weight_kg, anthropometry.height_cm, age, sex)

    metrics = BodyMetrics(
        id=uuid4(),
        anthropometry_id=anthropometry.id,
        bmi=bmi_val,
        bsa=bsa_val,
        bmr=bmr_val,
        method_bsa="Mosteller",
        method_bmr="Mifflin-St Jeor"
    )
    session.add(metrics)
