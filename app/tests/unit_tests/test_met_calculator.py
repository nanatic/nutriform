import pytest
from decimal import Decimal
from app.services.met_calculator import compute_met_minutes

class DummyQuestion:
    def __init__(self, text: str, order: int):
        self.question_text = text
        self.question_order = order


class DummyAnswer:
    def __init__(self, text, order, days_per_week=None, met_minutes=None):
        self.question = DummyQuestion(text, order)
        self.days_per_week = days_per_week
        self.met_minutes = met_minutes


def test_sedentary_question_is_weighted_x7():
    answers = [
        DummyAnswer("Сколько времени в день вы обычно проводите сидя", 1, met_minutes=1.2)
    ]
    assert compute_met_minutes(answers) == pytest.approx(8.4)


def test_regular_pairing():
    answers = [
        DummyAnswer("Сколько раз в неделю вы бегаете", 1, days_per_week=3),
        DummyAnswer("Сколько минут в день вы бегаете", 2, met_minutes=2.5),
    ]
    assert compute_met_minutes(answers) == pytest.approx(7.5)


def test_mixed_combination():
    answers = [
        DummyAnswer("Сколько раз в неделю вы плаваете", 1, days_per_week=2),
        DummyAnswer("Сколько минут в день вы плаваете", 2, met_minutes=3.0),
        DummyAnswer("Сколько времени в день вы обычно проводите сидя", 3, met_minutes=1.5)
    ]
    assert compute_met_minutes(answers) == pytest.approx(2*3.0 + 1.5*7)  # 6 + 10.5 = 16.5
