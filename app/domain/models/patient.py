from datetime import date
from enum import Enum
from pydantic import BaseModel, Field


class SexEnum(str, Enum):
    male = "male"
    female = "female"


class PatientCreate(BaseModel):
    full_name: str = Field(...)
    birth_date: date = Field(...)
    sex: SexEnum = Field(...)  # ✅ Используем Enum для валидации
    place_of_residence: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "full_name": "Иванов Иван Иванович",
                "birth_date": "1990-05-20",
                "sex": "male",
                "place_of_residence": "Москва"
            }
        }


class PatientRead(PatientCreate):
    id: int = Field(..., example=123456)
