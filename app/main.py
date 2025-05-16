import uuid
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, Body
from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.domain.models.anthropometry import AnthropometryCreate, AnthropometryRead
from app.domain.models.patient import PatientCreate, PatientRead
from app.domain.models.questionnaire import (
    QuestionnaireCreate, QuestionnaireRead, QuestionnaireUpdate,
    SubmissionCreate, SubmissionRead,
    AnswerCreate, QuestionCreate, QuestionRead, QuestionUpdate,
)
from app.domain.models.users import UserUpdate, ProfileChangeRequestCreate
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.body_metrics_repository import BodyMetricsRepository
from app.infrastructure.repositories.patient_repository import PatientRepository
from app.infrastructure.repositories.questionnaire_repository import QuestionnaireRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.use_cases.body_metrics_use_cases import BodyMetricsService
from app.use_cases.patient_use_cases import PatientService
from app.use_cases.questionnaire_use_cases import QuestionnaireService
from app.use_cases.user_use_cases import UserService
from app.utils.mailer import send_email

settings = get_settings()

app = FastAPI(
    title="Nutriform API",
    version="1.0.0",
    description="Сервис для работы с пациентами, опросниками и антропометрией"
)


# ── Dependencies ────────────────────────────────────────────

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))


def get_patient_service(db: Session = Depends(get_db)) -> PatientService:
    return PatientService(PatientRepository(db))


def get_questionnaire_service(db: Session = Depends(get_db)) -> QuestionnaireService:
    return QuestionnaireService(QuestionnaireRepository(db))


def get_body_metrics_service(db: Session = Depends(get_db)) -> BodyMetricsService:
    return BodyMetricsService(BodyMetricsRepository(db))


# ── Patients ───────────────────────────────────────────────

@app.post(
    "/patients/",
    response_model=int,
    status_code=status.HTTP_201_CREATED,
    summary="Создать пациента",
    description="Добавляет нового пациента и возвращает его уникальный ID.",
    tags=["Пациенты"],
)
def create_patient(
        data: PatientCreate = Body(
            ...,
            description="Данные нового пациента",
            example={"full_name": "Иван Иванов", "birth_date": "1990-05-20", "place_of_residence": "Москва"}
        ),
        svc: PatientService = Depends(get_patient_service),
):
    return svc.create_patient(data)


@app.get(
    "/patients/{patient_id}",
    response_model=PatientRead,
    summary="Получить пациента",
    description="Возвращает информацию о пациенте по его ID.",
    tags=["Пациенты"],
)
def read_patient(
        patient_id: int,
        svc: PatientService = Depends(get_patient_service),
):
    try:
        return svc.get_patient(patient_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Patient not found")


@app.get(
    "/patients/",
    response_model=List[PatientRead],
    summary="Список пациентов",
    description="Возвращает список всех пациентов.",
    tags=["Пациенты"],
)
def list_patients(
        svc: PatientService = Depends(get_patient_service),
):
    return svc.list_patients()


# ── Users ──────────────────────────────────────────────────

@app.put(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Редактировать профиль пользователя",
    description="Обновляет email, имя, должность или пароль пользователя.",
    tags=["Пользователи"],
)
def edit_user_profile(
        user_id: str,
        body: UserUpdate = Body(
            ...,
            description="Поля для обновления",
            example={"email": "new@example.com", "full_name": "Петр Петров"}
        ),
        svc: UserService = Depends(get_user_service),
):
    svc.edit_profile(user_id, body)


@app.post(
    "/users/{user_id}/profile-change",
    response_model=uuid.UUID,
    status_code=status.HTTP_201_CREATED,
    summary="Запрос на изменение профиля",
    description="Создает заявку на изменение полей профиля (уведомление администратору).",
    tags=["Пользователи"],
)
def request_profile_change(
        user_id: str,
        background_tasks: BackgroundTasks,
        body: ProfileChangeRequestCreate = Body(
            ...,
            description="Запрашиваемые поля и новые значения",
            example={"requested_fields": {"position": "Senior Nutritionist"}}
        ),
        svc: UserService = Depends(get_user_service),
):
    req_id = svc.request_profile_change(user_id, body)
    background_tasks.add_task(
        send_email,
        to_email=settings.admin_email,
        subject=f"[Nutriform] New profile-change request {req_id}",
        body=f"User {user_id} requested changes: {body.requested_fields}"
    )
    return req_id


# ── Questionnaires & Questions ────────────────────────────

@app.get(
    "/questionnaires/",
    response_model=List[QuestionnaireRead],
    summary="Список шаблонов опросников",
    description="Возвращает все шаблоны опросников.",
    tags=["Опросники"],
)
def list_questionnaires(
        svc: QuestionnaireService = Depends(get_questionnaire_service),
):
    return svc.list_questionnaires()


@app.post(
    "/questionnaires/",
    response_model=int,
    status_code=status.HTTP_201_CREATED,
    summary="Создать шаблон опросника",
    description="Добавляет новый шаблон опросника.",
    tags=["Опросники"],
)
def create_questionnaire(
        data: QuestionnaireCreate = Body(
            ...,
            description="Данные нового шаблона",
            example={"name": "Оценка питания", "type": "nutrition"}
        ),
        svc: QuestionnaireService = Depends(get_questionnaire_service),
):
    return svc.create_questionnaire(data)


@app.get(
    "/questionnaires/{qid}",
    response_model=QuestionnaireRead,
    summary="Получить шаблон опросника",
    description="Возвращает информацию о шаблоне по его ID.",
    tags=["Опросники"],
)
def read_questionnaire(
        qid: int,
        svc: QuestionnaireService = Depends(get_questionnaire_service),
):
    try:
        return svc.get_questionnaire(qid)
    except ValueError:
        raise HTTPException(status_code=404, detail="Questionnaire not found")


@app.put(
    "/questionnaires/{qid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Обновить шаблон опросника",
    description="Изменяет имя или тип шаблона опросника.",
    tags=["Опросники"],
)
def update_questionnaire(
        qid: int,
        data: QuestionnaireUpdate = Body(
            ...,
            description="Новые значения полей",
            example={"name": "Updated name"}
        ),
        svc: QuestionnaireService = Depends(get_questionnaire_service),
):
    try:
        svc.update_questionnaire(qid, data)
    except ValueError:
        raise HTTPException(status_code=404, detail="Questionnaire not found")


@app.delete(
    "/questionnaires/{qid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить шаблон опросника",
    description="Удаляет шаблон опросника по ID.",
    tags=["Опросники"],
)
def delete_questionnaire(
        qid: int,
        svc: QuestionnaireService = Depends(get_questionnaire_service),
):
    try:
        svc.delete_questionnaire(qid)
    except ValueError:
        raise HTTPException(status_code=404, detail="Questionnaire not found")


@app.get(
    "/questionnaires/{qid}/questions",
    response_model=List[QuestionRead],
    summary="Список вопросов опросника",
    description="Возвращает вопросы данного шаблона.",
    tags=["Опросники"],
)
def list_questions(
        qid: int,
        svc: QuestionnaireService = Depends(get_questionnaire_service),
):
    return svc.list_questions(qid)


@app.post(
    "/questionnaires/{qid}/questions",
    response_model=int,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить вопрос",
    description="Создает новый вопрос для указанного опросника.",
    tags=["Опросники"],
)
def create_question(
        qid: int,
        data: QuestionCreate = Body(
            ...,
            description="Данные нового вопроса",
            example={"questionnaire_id": 1, "question_text": "Как часто…", "question_order": 1}
        ),
        svc: QuestionnaireService = Depends(get_questionnaire_service),
):
    return svc.create_question(data.copy(update={"questionnaire_id": qid}))


@app.put(
    "/questions/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Обновить вопрос",
    description="Изменяет текст, порядок или дополнительные поля вопроса.",
    tags=["Опросники"],
)
def update_question(
        question_id: int,
        data: QuestionUpdate = Body(
            ...,
            description="Новые значения полей",
            example={"question_text": "Новый текст вопроса"}
        ),
        svc: QuestionnaireService = Depends(get_questionnaire_service),
):
    try:
        svc.update_question(question_id, data)
    except ValueError:
        raise HTTPException(status_code=404, detail="Question not found")


@app.delete(
    "/questions/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить вопрос",
    description="Удаляет вопрос по его ID.",
    tags=["Опросники"],
)
def delete_question(
        question_id: int,
        svc: QuestionnaireService = Depends(get_questionnaire_service),
):
    try:
        svc.delete_question(question_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Question not found")


# ── Submissions & Answers ──────────────────────────────────

@app.post(
    "/patients/{patient_id}/submissions/",
    response_model=uuid.UUID,
    status_code=status.HTTP_201_CREATED,
    summary="Создать submission",
    description="Сохраняет ответы пациента на все вопросы опросника.",
    tags=["Submissions"],
)
def create_submission(
        patient_id: int,
        data: SubmissionCreate = Body(
            ...,
            description="Тип опросника и ответы",
            example={"questionnaire_type": "nutrition", "responses": {"1": "never", "2": 3}}
        ),
        svc: QuestionnaireService = Depends(get_questionnaire_service),
):
    return svc.create_submission(patient_id, data)


@app.get(
    "/patients/{patient_id}/submissions/",
    response_model=List[SubmissionRead],
    summary="Список submissions",
    description="Возвращает все сохранённые ответы данного пациента.",
    tags=["Submissions"],
)
def get_submissions(
        patient_id: int,
        svc: QuestionnaireService = Depends(get_questionnaire_service),
):
    return svc.get_submissions(patient_id)


@app.post(
    "/submissions/{submission_id}/answers/",
    response_model=int,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить ответ",
    description="Добавляет отдельный ответ в существующий submission.",
    tags=["Submissions"],
)
def add_answer(
        submission_id: uuid.UUID,
        data: AnswerCreate = Body(
            ...,
            description="Поля ответа",
            example={"question_id": 1, "days_per_week": 5, "frequency_eat": "2-3 per day"}
        ),
        svc: QuestionnaireService = Depends(get_questionnaire_service),
):
    return svc.add_answer(submission_id, data)


# ── Anthropometry ─────────────────────────────────────────

@app.post(
    "/patients/{patient_id}/anthropometries/",
    response_model=uuid.UUID,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить антропометрию",
    description="Сохраняет рост, вес и сопутствующие показатели пациента.",
    tags=["Антропометрия"],
)
def add_anthropometry(
        patient_id: int,
        data: AnthropometryCreate = Body(
            ...,
            description="Антропометрические данные пациента",
            example={
                "height_cm": 175.5,
                "weight_kg": 70.2,
                "measured_at": "2025-05-14T10:30:00Z",
                "waist_cm": 80.0,
                "hip_cm": 95.0
            }
        ),
        svc: BodyMetricsService = Depends(get_body_metrics_service),
):
    return svc.add_anthropometry(patient_id, data)


@app.get(
    "/patients/{patient_id}/anthropometries/latest",
    response_model=AnthropometryRead,
    summary="Последняя антропометрия",
    description="Возвращает самые свежие антропометрические данные пациента.",
    tags=["Антропометрия"],
)
def get_latest_anthropometry(
        patient_id: int,
        svc: BodyMetricsService = Depends(get_body_metrics_service),
):
    res = svc.get_latest(patient_id)
    if not res:
        raise HTTPException(status_code=404, detail="No metrics found")
    return res
