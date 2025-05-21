import uuid
from enum import Enum
from typing import Dict, Any, List, Optional, Union

from pydantic import BaseModel, Field


class QuestionnaireCreate(BaseModel):
    name: str = Field(..., example="Оценка питания", description="Название опросника")
    type: str = Field(..., example="nutrition", description="Тип опросника: 'nutrition' или 'physical_activity'")

    class Config:
        schema_extra = {
            "example": {
                "name": "Оценка питания",
                "type": "nutrition"
            }
        }


class QuestionnaireUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Оценка физической активности", description="Новое название опросника")
    type: Optional[str] = Field(None, example="physical_activity", description="Новый тип опросника")


class QuestionnaireRead(BaseModel):
    id: int = Field(..., description="Идентификатор опросника")
    name: str = Field(..., description="Название опросника")
    type: str = Field(..., description="Тип опросника")


class QuestionCreate(BaseModel):
    questionnaire_id: int = Field(..., example=1, description="ID связанного опросника")
    question_text: str = Field(..., example="Как часто вы едите овощи?", description="Текст вопроса")
    question_order: Optional[int] = Field(None, example=1, description="Порядок отображения вопроса")
    answers_json: Optional[Dict[str, Any]] = Field(
        None,
        example={"a": "Ежедневно", "b": "Редко"},
        description="Возможные ответы в формате JSON"
    )
    food_group_id: Optional[int] = Field(None, example=5, description="ID группы продуктов (если применимо)")
    portion_description: Optional[str] = Field(None, example="Одна чашка нарезанных овощей",
                                               description="Описание порции")


class QuestionRead(BaseModel):
    id: int = Field(..., description="Идентификатор вопроса")
    questionnaire_id: int = Field(..., description="Идентификатор опросника")
    question_text: str = Field(..., description="Текст вопроса")
    question_order: Optional[int] = Field(None, description="Порядок отображения вопроса")
    answers_json: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    food_group_id: Optional[int] = Field(None, description="ID группы продуктов")
    portion_description: Optional[str] = Field(None, description="Описание порции")


class QuestionUpdate(BaseModel):
    question_text: Optional[str] = Field(None, example="Как часто вы занимаетесь спортом?",
                                         description="Новый текст вопроса")
    question_order: Optional[int] = Field(None, example=2, description="Новый порядок отображения вопроса")
    answers_json: Optional[Dict[str, Any]] = Field(None, example={"a": "Каждый день", "b": "Редко"},
                                                   description="Обновленные ответы")
    food_group_id: Optional[int] = Field(None, example=7, description="Новый ID группы продуктов")
    portion_description: Optional[str] = Field(None, example="Половина порции", description="Новое описание порции")


class SubmissionCreate(BaseModel):
    questionnaire_type: str = Field(..., example="nutrition",
                                    description="Тип опросника: 'nutrition' или 'physical_activity'")
    responses: Dict[str, Any] = Field(..., example={"q1": "a", "q2": "b"},
                                      description="Ответы в формате JSON, где ключ — ID вопроса")


class SubmissionRead(BaseModel):
    id: uuid.UUID = Field(..., description="UUID записи о прохождении опроса")
    patient_id: int = Field(..., example=123, description="ID пациента")
    questionnaire_type: str = Field(..., example="nutrition", description="Тип опросника")
    responses: Dict[str, Any] = Field(..., example={"q1": "a", "q2": "b"}, description="Ответы пациента")
    total_met_minutes: Optional[float] = Field(None, description="Суммарные MET-минуты в неделю")


class FrequencyEnum(str, Enum):
    never = 'never'
    m1_3 = '1-3 per month'
    w1 = '1 per week'
    w2_4 = '2-4 per week'
    d1 = '1 per day'
    d2_3 = '2-3 per day'
    d4p = '4+ per day'


class AnswerCreate(BaseModel):
    question_id: int = Field(..., example=10, description="ID вопроса")
    days_per_week: Optional[int] = Field(None, example=3, description="Количество дней в неделю (если применимо)")
    met_minutes: Optional[float] = Field(None, example=150.0, description="Количество MET-минут (если применимо)")
    frequency_eat: Optional[FrequencyEnum] = Field(None, example="Ежедневно", description="Частота употребления продукта")


class AnswerRead(BaseModel):
    id: int = Field(..., description="Идентификатор ответа")
    submission_id: uuid.UUID = Field(..., description="UUID связанного опроса (submission)")
    question_id: int = Field(..., description="ID вопроса")
    days_per_week: Optional[int] = Field(None, description="Количество дней в неделю")
    met_minutes: Optional[float] = Field(None, description="Количество MET-минут")
    frequency_eat: Optional[str] = Field(None, description="Частота употребления продукта")
