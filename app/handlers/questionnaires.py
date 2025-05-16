import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app.domain.models.questionnaire import (
    QuestionnaireCreate, QuestionnaireRead, QuestionnaireUpdate,
    QuestionCreate, QuestionRead, QuestionUpdate,
    SubmissionCreate, SubmissionRead, AnswerCreate,
)
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.questionnaire_repository import QuestionnaireRepository
from app.use_cases.questionnaire_use_cases import QuestionnaireService

router = APIRouter(tags=["Опросники"])

# ── DEPENDENCY ────────────────────────────────────────────
def get_service(db: Session = Depends(get_db)) -> QuestionnaireService:
    return QuestionnaireService(QuestionnaireRepository(db))


# ── Шаблоны опросников ───────────────────────────────────
@router.get(
    "/questionnaires/",
    response_model=List[QuestionnaireRead],
    summary="Список шаблонов опросников"
)
def list_questionnaires(svc: QuestionnaireService = Depends(get_service)):
    return svc.list_questionnaires()


@router.post(
    "/questionnaires/",
    response_model=int,
    status_code=status.HTTP_201_CREATED,
    summary="Создать шаблон опросника"
)
def create_questionnaire(
    data: QuestionnaireCreate = Body(...),
    svc: QuestionnaireService = Depends(get_service),
):
    return svc.create_questionnaire(data)


@router.get(
    "/questionnaires/{qid}",
    response_model=QuestionnaireRead,
    summary="Получить шаблон опросника"
)
def read_questionnaire(
    qid: int,
    svc: QuestionnaireService = Depends(get_service),
):
    try:
        return svc.get_questionnaire(qid)
    except ValueError:
        raise HTTPException(status_code=404, detail="Questionnaire not found")


@router.put(
    "/questionnaires/{qid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Обновить шаблон опросника"
)
def update_questionnaire(
    qid: int,
    data: QuestionnaireUpdate = Body(...),
    svc: QuestionnaireService = Depends(get_service),
):
    try:
        svc.update_questionnaire(qid, data)
    except ValueError:
        raise HTTPException(status_code=404, detail="Questionnaire not found")


@router.delete(
    "/questionnaires/{qid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить шаблон опросника"
)
def delete_questionnaire(
    qid: int,
    svc: QuestionnaireService = Depends(get_service),
):
    try:
        svc.delete_questionnaire(qid)
    except ValueError:
        raise HTTPException(status_code=404, detail="Questionnaire not found")


# ── Вопросы ───────────────────────────────────────────────
@router.get(
    "/questionnaires/{qid}/questions",
    response_model=List[QuestionRead],
    summary="Список вопросов опросника"
)
def list_questions(
    qid: int,
    svc: QuestionnaireService = Depends(get_service),
):
    return svc.list_questions(qid)


@router.post(
    "/questionnaires/{qid}/questions",
    response_model=int,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить вопрос"
)
def create_question(
    qid: int,
    data: QuestionCreate = Body(...),
    svc: QuestionnaireService = Depends(get_service),
):
    return svc.create_question(data.copy(update={"questionnaire_id": qid}))


@router.put(
    "/questions/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Обновить вопрос"
)
def update_question(
    question_id: int,
    data: QuestionUpdate = Body(...),
    svc: QuestionnaireService = Depends(get_service),
):
    try:
        svc.update_question(question_id, data)
    except ValueError:
        raise HTTPException(status_code=404, detail="Question not found")


@router.delete(
    "/questions/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить вопрос"
)
def delete_question(
    question_id: int,
    svc: QuestionnaireService = Depends(get_service),
):
    try:
        svc.delete_question(question_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Question not found")


# ── Submissions & Answers (тоже сюда) ─────────────────────
@router.post(
    "/patients/{patient_id}/submissions/",
    response_model=uuid.UUID,
    status_code=status.HTTP_201_CREATED,
    tags=["Submissions"],
    summary="Создать submission"
)
def create_submission(
    patient_id: int,
    data: SubmissionCreate = Body(...),
    svc: QuestionnaireService = Depends(get_service),
):
    return svc.create_submission(patient_id, data)


@router.get(
    "/patients/{patient_id}/submissions/",
    response_model=List[SubmissionRead],
    tags=["Submissions"],
    summary="Список submissions пациента"
)
def get_submissions(
    patient_id: int,
    svc: QuestionnaireService = Depends(get_service),
):
    return svc.get_submissions(patient_id)


@router.post(
    "/submissions/{submission_id}/answers/",
    response_model=int,
    status_code=status.HTTP_201_CREATED,
    tags=["Submissions"],
    summary="Добавить ответ в submission"
)
def add_answer(
    submission_id: uuid.UUID,
    data: AnswerCreate = Body(...),
    svc: QuestionnaireService = Depends(get_service),
):
    return svc.add_answer(submission_id, data)
