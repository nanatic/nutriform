import uuid
from fastapi import APIRouter, Depends, status, Body
from typing import List
from app.domain.models.questionnaire import SubmissionCreate, SubmissionRead, AnswerCreate
from app.use_cases.questionnaire_use_cases import QuestionnaireService
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.questionnaire_repository import QuestionnaireRepository
from sqlalchemy.orm import Session

router = APIRouter(tags=["Submissions"])

def get_service(db: Session = Depends(get_db)) -> QuestionnaireService:
    return QuestionnaireService(QuestionnaireRepository(db))

@router.post("/patients/{patient_id}/submissions/", response_model=uuid.UUID, status_code=status.HTTP_201_CREATED, summary="Создать submission")
def create_submission(patient_id: int, data: SubmissionCreate = Body(...), svc: QuestionnaireService = Depends(get_service)):
    return svc.create_submission(patient_id, data)

@router.get("/patients/{patient_id}/submissions/", response_model=List[SubmissionRead], summary="Список submissions пациента")
def get_submissions(patient_id: int, svc: QuestionnaireService = Depends(get_service)):
    return svc.get_submissions(patient_id)

@router.post("/submissions/{submission_id}/answers/", response_model=int, status_code=status.HTTP_201_CREATED, summary="Добавить ответ в submission")
def add_answer(submission_id: uuid.UUID, data: AnswerCreate = Body(...), svc: QuestionnaireService = Depends(get_service)):
    return svc.add_answer(submission_id, data)
