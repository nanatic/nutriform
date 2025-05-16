from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.domain.models.patient import PatientRead
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.user_repository import UserRepository
from app.use_cases.user_use_cases import UserService

router = APIRouter(prefix="/users/doctors", tags=["Доктора"])


def get_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))


@router.post("/{doctor_id}/patients/{patient_id}", status_code=status.HTTP_204_NO_CONTENT,
             summary="Прикрепить пациента к доктору")
def link_patient(doctor_id: str, patient_id: int, svc: UserService = Depends(get_service)):
    svc.add_patient(doctor_id, patient_id)


@router.delete("/{doctor_id}/patients/{patient_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Открепить пациента от доктора")
def unlink_patient(doctor_id: str, patient_id: int, svc: UserService = Depends(get_service)):
    svc.remove_patient(doctor_id, patient_id)


@router.get("/{doctor_id}/patients", response_model=List[PatientRead], summary="Список пациентов доктора")
def list_patients(doctor_id: str, svc: UserService = Depends(get_service)):
    return svc.list_patients(doctor_id)


@router.get("/{doctor_id}/patients/search", response_model=List[PatientRead], summary="Поиск пациентов доктора")
def search_patients(doctor_id: str, full_name: str | None = Query(None), birth_date: str | None = Query(None),
                    svc: UserService = Depends(get_service)):
    return svc.search_patients(doctor_id, {"full_name": full_name, "birth_date": birth_date})


@router.get("/{doctor_id}/stats", summary="Статистика доктора")
def doctor_stats(doctor_id: str, all_patients: bool = Query(False), svc: UserService = Depends(get_service)):
    return svc.stats(doctor_id, all_patients)
