from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class AnthropometryCreate(BaseModel):
    height_cm: float
    weight_kg: float
    measured_at: datetime
    waist_cm: Optional[float] = None
    hip_cm: Optional[float] = None


class AnthropometryRead(AnthropometryCreate):
    id: UUID  # ← Используем UUID, а не str
    height_cm: float
    weight_kg: float
    measured_at: datetime
    patient_id: int
    waist_cm: Optional[float] = None
    hip_cm: Optional[float] = None

    class Config:
        from_attributes = True  # В новых версиях Pydantic
        json_encoders = {
            UUID: lambda v: str(v)
        }
