from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
import uuid
from typing import List, Dict, Any

from app.infrastructure.db.models import (
    Questionnaires,
    QuestionnaireQuestions,
    QuestionnaireSubmissions,
    QuestionnaireAnswers,
)
from app.domain.models.questionnaire import (
    QuestionnaireCreate, QuestionnaireUpdate,
    QuestionCreate, QuestionUpdate, QuestionnaireRead, QuestionRead
)
from app.domain.repositories.questionnaire_repository_interface import IQuestionnaireRepository


class QuestionnaireRepository(IQuestionnaireRepository):
    def __init__(self, session: Session):
        self.session = session

    # — шаблоны —
    def create_questionnaire(self, data: QuestionnaireCreate) -> int:
        q = Questionnaires(name=data.name, type=data.type)
        self.session.add(q)
        self.session.commit()
        return q.id

    def get_questionnaire(self, questionnaire_id: int) -> QuestionnaireRead | None:
        q = self.session.get(Questionnaires, questionnaire_id)
        return q.__dict__ if q else None

    def update_questionnaire(self, questionnaire_id: int, data: QuestionnaireUpdate) -> None:
        q = self.session.get(Questionnaires, questionnaire_id)
        if not q:
            raise NoResultFound()
        for field, val in data.dict(exclude_unset=True).items():
            setattr(q, field, val)
        self.session.commit()

    def delete_questionnaire(self, questionnaire_id: int) -> None:
        q = self.session.get(Questionnaires, questionnaire_id)
        if not q:
            raise NoResultFound()
        self.session.delete(q)
        self.session.commit()

    def list_questionnaires(self) -> List[Dict[str, Any]]:
        qs = self.session.query(Questionnaires).all()
        return [q.__dict__ for q in qs]

    # — вопросы —
    def create_question(self, data: QuestionCreate) -> int:
        qq = QuestionnaireQuestions(**data.dict())
        self.session.add(qq)
        self.session.commit()
        return qq.id

    def get_questions(self, questionnaire_id: int) -> List[QuestionRead]:
        qs = (
            self.session.query(QuestionnaireQuestions)
            .filter_by(questionnaire_id=questionnaire_id)
            .order_by(QuestionnaireQuestions.question_order)
            .all()
        )
        return [QuestionRead(**q.__dict__) for q in qs]

    def update_question(self, question_id: int, data: QuestionUpdate) -> None:
        qq = self.session.get(QuestionnaireQuestions, question_id)
        if not qq:
            raise NoResultFound()
        for field, val in data.dict(exclude_unset=True).items():
            setattr(qq, field, val)
        self.session.commit()

    def delete_question(self, question_id: int) -> None:
        qq = self.session.get(QuestionnaireQuestions, question_id)
        if not qq:
            raise NoResultFound()
        self.session.delete(qq)
        self.session.commit()

    def list_questions(self, questionnaire_id: int) -> List[Dict[str, Any]]:
        qs = self.session.query(QuestionnaireQuestions).filter_by(questionnaire_id=questionnaire_id).all()
        return [q.__dict__ for q in qs]

    def get_question(self, question_id: int) -> Dict[str, Any]:
        q = self.session.get(QuestionnaireQuestions, question_id)
        if not q:
            raise ValueError("Question not found")
        return q.__dict__

    def create_question(self, data: QuestionCreate) -> int:
        q = QuestionnaireQuestions(**data.dict())
        self.session.add(q)
        self.session.commit()
        return q.id

    def update_question(self, question_id: int, data: QuestionUpdate) -> None:
        q = self.session.get(QuestionnaireQuestions, question_id)
        if not q:
            raise ValueError("Question not found")
        for field, val in data.dict(exclude_unset=True).items():
            setattr(q, field, val)
        self.session.commit()

    def delete_question(self, question_id: int) -> None:
        q = self.session.get(QuestionnaireQuestions, question_id)
        if not q:
            raise ValueError("Question not found")
        self.session.delete(q)
        self.session.commit()

    # ——— Submissions и Answers ——— (существующие) — версии без изменений —
    def create_submission(self, patient_id: int, questionnaire_type: str, responses: Dict[str, Any]) -> uuid.UUID:
        submission = QuestionnaireSubmissions(id=uuid.uuid4(), patient_id=patient_id,
                                              questionnaire_type=questionnaire_type, responses=responses)
        self.session.add(submission)
        self.session.commit()
        return submission.id

    def get_submissions_by_patient(self, patient_id: int) -> List[Dict[str, Any]]:
        subs = self.session.query(QuestionnaireSubmissions).filter_by(patient_id=patient_id).all()
        return [s.__dict__ for s in subs]

    def add_answer(self, submission_id: uuid.UUID, question_id: int, answer_data: Dict[str, Any]) -> int:
        answer_data.pop("question_id", None)
        ans = QuestionnaireAnswers(submission_id=submission_id, question_id=question_id, **answer_data)
        self.session.add(ans)
        self.session.commit()
        return ans.id