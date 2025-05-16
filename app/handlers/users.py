import uuid
from typing import List

from fastapi import APIRouter, Depends, status, Body, BackgroundTasks
from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.domain.models.users import UserUpdate, ProfileChangeRequestCreate, NotificationRead
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.user_repository import UserRepository
from app.use_cases.user_use_cases import UserService

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
    description="Обновляет email, логин, должность или пароль."
)
def edit_user_profile(
        user_id: uuid.UUID,
        body: UserUpdate = Body(
            ...,
            example={"email": "new@example.com", "login": "new_login"},
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
        body: ProfileChangeRequestCreate = Body(
            ...,
            example={"requested_fields": {"position": "Senior Nutritionist"}},
            description="Ключи и новые значения"
        ),
        svc: UserService = Depends(get_user_service),
):
    req_id = svc.request_profile_change(user_id, body)
    return req_id


@router.get(
    "/{user_id}/notifications",
    response_model=List[NotificationRead],
    summary="Получить уведомления пользователя",
)
def get_notifications(
        user_id: uuid.UUID,
        svc: UserService = Depends(get_user_service),
):
    return svc.get_notifications(user_id)
