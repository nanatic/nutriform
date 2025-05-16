from typing import List
import uuid

from app.domain.repositories.questionnaire_repository_interface import IQuestionnaireRepository
from app.domain.models.questionnaire import (
    QuestionnaireCreate, QuestionnaireRead, QuestionnaireUpdate,
    QuestionCreate, QuestionRead, QuestionUpdate,
    SubmissionCreate, SubmissionRead,
    AnswerCreate, AnswerRead,
)

class QuestionnaireService:
    def __init__(self, repo: IQuestionnaireRepository):
        self.repo = repo

    # ——— Шаблоны опросников ———
    def list_questionnaires(self) -> List[QuestionnaireRead]:
        return [QuestionnaireRead(**q) for q in self.repo.list_questionnaires()]

    def get_questionnaire(self, questionnaire_id: int) -> QuestionnaireRead:
        return QuestionnaireRead(**self.repo.get_questionnaire(questionnaire_id))

    def create_questionnaire(self, data: QuestionnaireCreate) -> int:
        return self.repo.create_questionnaire(data)

    def update_questionnaire(self, questionnaire_id: int, data: QuestionnaireUpdate) -> None:
        self.repo.update_questionnaire(questionnaire_id, data)

    def delete_questionnaire(self, questionnaire_id: int) -> None:
        self.repo.delete_questionnaire(questionnaire_id)

    # ——— Вопросы ———
    def list_questions(self, questionnaire_id: int) -> List[QuestionRead]:
        return [QuestionRead(**q) for q in self.repo.list_questions(questionnaire_id)]

    def get_question(self, question_id: int) -> QuestionRead:
        return QuestionRead(**self.repo.get_question(question_id))

    def create_question(self, data: QuestionCreate) -> int:
        return self.repo.create_question(data)

    def update_question(self, question_id: int, data: QuestionUpdate) -> None:
        self.repo.update_question(question_id, data)

    def delete_question(self, question_id: int) -> None:
        self.repo.delete_question(question_id)

    # ——— Submissions и Answers ———
    def create_submission(self, patient_id: int, data: SubmissionCreate) -> uuid.UUID:
        return self.repo.create_submission(patient_id, data.questionnaire_type, data.responses)

    def get_submissions(self, patient_id: int) -> List[SubmissionRead]:
        return [SubmissionRead(**s) for s in self.repo.get_submissions_by_patient(patient_id)]

    def add_answer(self, submission_id: uuid.UUID, data: AnswerCreate) -> int:
        return self.repo.add_answer(submission_id, data.question_id, data.dict(exclude_unset=True))
