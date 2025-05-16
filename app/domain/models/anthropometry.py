from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AnthropometryCreate(BaseModel):
    height_cm: float
    weight_kg: float
    measured_at: datetime
    waist_cm: Optional[float] = None
    hip_cm: Optional[float] = None


class AnthropometryRead(AnthropometryCreate):
    id: str  # UUID as str
