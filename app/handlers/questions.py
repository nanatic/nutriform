from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List
from app.domain.models.questionnaire import QuestionCreate, QuestionRead, QuestionUpdate
from app.use_cases.questionnaire_use_cases import QuestionnaireService
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.questionnaire_repository import QuestionnaireRepository
from sqlalchemy.orm import Session

router = APIRouter(tags=["Вопросы"])

def get_service(db: Session = Depends(get_db)) -> QuestionnaireService:
    return QuestionnaireService(QuestionnaireRepository(db))

@router.get("/questionnaires/{qid}/questions", response_model=List[QuestionRead], summary="Список вопросов опросника")
def list_questions(qid: int, svc: QuestionnaireService = Depends(get_service)):
    return svc.list_questions(qid)

@router.post("/questionnaires/{qid}/questions", response_model=int, status_code=status.HTTP_201_CREATED, summary="Добавить вопрос")
def create_question(qid: int, data: QuestionCreate = Body(...), svc: QuestionnaireService = Depends(get_service)):
    return svc.create_question(data.copy(update={"questionnaire_id": qid}))

@router.put("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Обновить вопрос")
def update_question(question_id: int, data: QuestionUpdate = Body(...), svc: QuestionnaireService = Depends(get_service)):
    try:
        svc.update_question(question_id, data)
    except ValueError:
        raise HTTPException(status_code=404, detail="Question not found")

@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить вопрос")
def delete_question(question_id: int, svc: QuestionnaireService = Depends(get_service)):
    try:
        svc.delete_question(question_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Question not found")
