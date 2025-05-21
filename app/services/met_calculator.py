from decimal import Decimal
from typing import List

from sqlalchemy.orm import Session

from app.infrastructure.db.models import QuestionnaireAnswers
from app.infrastructure.db.models import QuestionnaireSubmissions

SITTING_QUESTION_KEYWORDS = [
    "сколько времени в день вы обычно проводите сидя"
]

__all__ = ["compute_met_minutes", "update_submission_met_minutes"]
def is_sedentary(question_text: str) -> bool:
    return any(kw.lower() in question_text.lower() for kw in SITTING_QUESTION_KEYWORDS)


def compute_met_minutes(answers: List[QuestionnaireAnswers]) -> float:
    total = Decimal("0.0")
    paired = []

    answers_sorted = sorted(answers, key=lambda a: a.question.question_order or 0)

    i = 0
    while i < len(answers_sorted):
        ans = answers_sorted[i]
        q_text = ans.question.question_text if ans.question else ""

        if is_sedentary(q_text) and ans.met_minutes:
            total += Decimal(ans.met_minutes) * 7
            i += 1
            continue

        if ans.days_per_week and i + 1 < len(answers_sorted):
            next_ans = answers_sorted[i + 1]
            if next_ans.met_minutes:
                total += Decimal(ans.days_per_week) * Decimal(next_ans.met_minutes)
                i += 2
                continue

        i += 1  # неудачная пара, просто идем дальше

    return float(total)


def update_submission_met_minutes(session: Session, submission_id, answers: List[QuestionnaireAnswers]):
    total = compute_met_minutes(answers)
    submission = session.get(QuestionnaireSubmissions, submission_id)
    if not submission:
        raise ValueError("Submission not found")
    submission.total_met_minutes = total
    session.commit()
