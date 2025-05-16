import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app.domain.models.anthropometry import AnthropometryCreate, AnthropometryRead
from app.use_cases.body_metrics_use_cases import BodyMetricsService
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.body_metrics_repository import BodyMetricsRepository

router = APIRouter(tags=["Антропометрия"])

def get_service(db: Session = Depends(get_db)) -> BodyMetricsService:
    return BodyMetricsService(BodyMetricsRepository(db))

@router.post(
    "/patients/{patient_id}/anthropometries/",
    response_model=uuid.UUID,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить антропометрию"
)
def add_anthropometry(
    patient_id: int,
    data: AnthropometryCreate = Body(
        ...,
        example={
            "height_cm": 170.0,
            "weight_kg": 65.3,
            "measured_at": "2025-05-14T10:30:00Z"
        }
    ),
    svc: BodyMetricsService = Depends(get_service),
):
    return svc.add_anthropometry(patient_id, data)

@router.get(
    "/patients/{patient_id}/anthropometries/latest",
    response_model=AnthropometryRead,
    summary="Последняя антропометрия"
)
def get_latest(
    patient_id: int,
    svc: BodyMetricsService = Depends(get_service),
):
    res = svc.get_latest(patient_id)
    if not res:
        raise HTTPException(status_code=404, detail="No metrics found")
    return res
