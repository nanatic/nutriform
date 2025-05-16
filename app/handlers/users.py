from typing import List, Dict, Any
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Body, BackgroundTasks, Query
from sqlalchemy.orm import Session

from app.domain.models.patient import PatientRead
from app.domain.models.users import UserUpdate, ProfileChangeRequestCreate
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.user_repository import UserRepository
from app.use_cases.user_use_cases import UserService
from app.utils.mailer import send_email
from app.config.settings import get_settings

settings = get_settings()

router = APIRouter(prefix="/users", tags=["Пользователи"])


# ── DEPENDENCY ────────────────────────────────────────────
def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))


# ── Профиль пользователя ─────────────────────────────────
@router.put(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Редактировать профиль пользователя",
    description="Обновляет email, ФИО, должность или пароль."
)
def edit_user_profile(
    user_id: str,
    body: UserUpdate = Body(
        ...,
        example={"email": "new@example.com", "full_name": "Новый Имя"},
        description="Поле/поля, которые нужно изменить"
    ),
    svc: UserService = Depends(get_user_service),
):
    svc.edit_profile(user_id, body)


@router.post(
    "/{user_id}/profile-change",
    response_model=uuid.UUID,
    status_code=status.HTTP_201_CREATED,
    summary="Создать запрос на изменение профиля",
    description="Сохраняет запрос и уведомляет администратора по email."
)
async def request_profile_change(
    user_id: str,
    background_tasks: BackgroundTasks,
    body: ProfileChangeRequestCreate = Body(
        ...,
        example={"requested_fields": {"position": "Senior Nutritionist"}},
        description="Ключи и новые значения"
    ),
    svc: UserService = Depends(get_user_service),
):
    req_id = svc.request_profile_change(user_id, body)
    background_tasks.add_task(
        send_email,
        to_email=settings.admin_email,
        subject=f"[Nutriform] Profile-change request {req_id}",
        body=f"User {user_id} requested: {body.requested_fields}"
    )
    return req_id


# ── «Доктор ↔ Пациенты» ──────────────────────────────────
@router.post(
    "/doctors/{doctor_id}/patients/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Прикрепить пациента к доктору",
    tags=["Доктора"]
)
def link_patient(
    doctor_id: str,
    patient_id: int,
    svc: UserService = Depends(get_user_service),
):
    svc.add_patient(doctor_id, patient_id)


@router.delete(
    "/doctors/{doctor_id}/patients/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Открепить пациента от доктора",
    tags=["Доктора"]
)
def unlink_patient(
    doctor_id: str,
    patient_id: int,
    svc: UserService = Depends(get_user_service),
):
    svc.remove_patient(doctor_id, patient_id)


@router.get(
    "/doctors/{doctor_id}/patients",
    response_model=List[PatientRead],
    summary="Список пациентов доктора",
    tags=["Доктора"]
)
def list_my_patients(
    doctor_id: str,
    svc: UserService = Depends(get_user_service),
):
    return svc.list_patients(doctor_id)


@router.get(
    "/doctors/{doctor_id}/patients/search",
    response_model=List[PatientRead],
    summary="Поиск пациентов доктора",
    tags=["Доктора"]
)
def search_my_patients(
    doctor_id: str,
    full_name: str | None = Query(None, example="Иван"),
    birth_date: str | None = Query(None, example="1990-05-20"),
    svc: UserService = Depends(get_user_service),
):
    return svc.search_patients(doctor_id, {"full_name": full_name, "birth_date": birth_date})


@router.get(
    "/doctors/{doctor_id}/stats",
    summary="Статистика доктора",
    tags=["Доктора"]
)
def doctor_stats(
    doctor_id: str,
    all_patients: bool = Query(False, description="Учесть всех пациентов в базе?"),
    svc: UserService = Depends(get_user_service),
):
    return svc.stats(doctor_id, all_patients)
