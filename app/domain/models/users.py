from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, RootModel


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    login: Optional[str] = None
    password: Optional[str] = None  # если будете менять пароль


class ProfileChangeRequestCreate(BaseModel):
    requested_fields: Dict[str, Any]


class NotificationRead(BaseModel):
    id: int = Field(..., example=1)
    user_id: UUID
    message: str = Field(..., example="Ваш запрос одобрен")
    created_at: datetime = Field(..., example="2025-05-16T10:00:00Z")
    read: bool = Field(..., example=False)


class NotificationList(RootModel[List[NotificationRead]]):
    pass
