from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List
from app.domain.models.questionnaire import QuestionnaireCreate, QuestionnaireRead, QuestionnaireUpdate
from app.use_cases.questionnaire_use_cases import QuestionnaireService
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.questionnaire_repository import QuestionnaireRepository
from sqlalchemy.orm import Session

router = APIRouter(prefix="/questionnaires", tags=["Опросники"])

def get_service(db: Session = Depends(get_db)) -> QuestionnaireService:
    return QuestionnaireService(QuestionnaireRepository(db))

@router.get("/", response_model=List[QuestionnaireRead], summary="Список шаблонов опросников")
def list_questionnaires(svc: QuestionnaireService = Depends(get_service)):
    return svc.list_questionnaires()

@router.post("/", response_model=int, status_code=status.HTTP_201_CREATED, summary="Создать шаблон опросника")
def create_questionnaire(data: QuestionnaireCreate = Body(...), svc: QuestionnaireService = Depends(get_service)):
    return svc.create_questionnaire(data)

@router.get("/{qid}", response_model=QuestionnaireRead, summary="Получить шаблон опросника")
def read_questionnaire(qid: int, svc: QuestionnaireService = Depends(get_service)):
    try:
        return svc.get_questionnaire(qid)
    except ValueError:
        raise HTTPException(status_code=404, detail="Questionnaire not found")

@router.put("/{qid}", status_code=status.HTTP_204_NO_CONTENT, summary="Обновить шаблон опросника")
def update_questionnaire(qid: int, data: QuestionnaireUpdate = Body(...), svc: QuestionnaireService = Depends(get_service)):
    try:
        svc.update_questionnaire(qid, data)
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(status_code=404, detail=msg)
        if "Invalid questionnaire type" in msg:
            raise HTTPException(status_code=400, detail=msg)
        raise HTTPException(status_code=500, detail="Unexpected error")

@router.delete("/{qid}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить шаблон опросника")
def delete_questionnaire(qid: int, svc: QuestionnaireService = Depends(get_service)):
    try:
        svc.delete_questionnaire(qid)
    except ValueError:
        raise HTTPException(status_code=404, detail="Questionnaire not found")