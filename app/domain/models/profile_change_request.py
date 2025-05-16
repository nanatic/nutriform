from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProfileChangeRequestRead(BaseModel):
    id: UUID = Field(..., description="UUID заявки")
    user_id: UUID = Field(..., description="UUID пользователя")
    requested_fields: Dict[str, Any] = Field(..., description="Поля и новые значения")
    status: str = Field(..., description="Статус заявки: pending|approved|rejected")
    submitted_at: datetime = Field(..., description="Когда подана заявка")
    reviewed_by: Optional[UUID] = Field(None, description="UUID администратора, рассмотревшего заявку")
