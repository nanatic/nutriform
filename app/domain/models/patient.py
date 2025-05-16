from datetime import date

from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    full_name: str = Field(..., example="Иван Иванов")
    birth_date: date = Field(..., example="1990-05-20")
    place_of_residence: str = Field(..., example="Москва")

    class Config:
        schema_extra = {
            "example": {
                "full_name": "Иван Иванов",
                "birth_date": "1990-05-20",
                "place_of_residence": "Москва"
            }
        }


class PatientRead(PatientCreate):
    id: int = Field(..., example=123456)
