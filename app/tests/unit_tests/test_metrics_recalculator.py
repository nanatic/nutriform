from datetime import datetime, date, timedelta

import pytest

from app.formulas import bmi, Sex
from app.infrastructure.db.models import BodyMetrics
from app.services.metrics_recalculator import recompute_body_metrics


class DummyPatient:
    def __init__(self, birth_date, sex):
        self.birth_date = birth_date
        self.sex = sex


class DummyAnthropometry:
    def __init__(self, id_, height_cm, weight_kg, measured_at, patient):
        self.id = id_
        self.height_cm = height_cm
        self.weight_kg = weight_kg
        self.measured_at = measured_at
        self.patient = patient


class DummySession:
    def __init__(self):
        self.added = []

    def add(self, obj):
        self.added.append(obj)


def test_recompute_body_metrics_adds_metrics():
    birth = date.today() - timedelta(days=30 * 365)
    patient = DummyPatient(birth_date=birth, sex=Sex.MALE)
    anthropometry = DummyAnthropometry(
        id_="123e4567-e89b-12d3-a456-426614174000",
        height_cm=180.0,
        weight_kg=80.0,
        measured_at=datetime.now(),
        patient=patient
    )
    session = DummySession()
    recompute_body_metrics(session, anthropometry)
    assert len(session.added) == 1
    metrics = session.added[0]
    assert isinstance(metrics, BodyMetrics)
    expected_bmi = bmi(80.0, 180.0)
    assert pytest.approx(metrics.bmi, rel=1e-6) == expected_bmi
    assert metrics.anthropometry_id == anthropometry.id
