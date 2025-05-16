from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class NotificationRead(BaseModel):
    id: int = Field(..., description="ID уведомления")
    user_id: UUID = Field(..., description="UUID пользователя")
    message: str = Field(..., description="Текст уведомления")
    created_at: datetime = Field(..., description="Время создания уведомления")
    is_read: bool = Field(..., description="Прочитано ли уведомление")
