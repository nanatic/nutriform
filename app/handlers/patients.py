from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app.domain.models.patient import PatientCreate, PatientRead
from app.infrastructure.db.session import get_db
from app.use_cases.patient_use_cases import PatientService

router = APIRouter(prefix="/patients", tags=["Пациенты"])


def get_patient_service(db: Session = Depends(get_db)) -> PatientService:
    from app.infrastructure.repositories.patient_repository import PatientRepository
    return PatientService(PatientRepository(db))


@router.post(
    "/",
    response_model=int,
    status_code=status.HTTP_201_CREATED,
    summary="Создать пациента"
)
def create_patient(
        data: PatientCreate = Body(...),
        svc: PatientService = Depends(get_patient_service),
):
    return svc.create_patient(data)


@router.get(
    "/{patient_id}",
    response_model=PatientRead,
    summary="Получить пациента"
)
def read_patient(
        patient_id: int,
        svc: PatientService = Depends(get_patient_service),
):
    try:
        return svc.get_patient(patient_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Patient not found")


@router.get(
    "/",
    response_model=List[PatientRead],
    summary="Список пациентов"
)
def list_patients(
        svc: PatientService = Depends(get_patient_service),
):
    return svc.list_patients()
