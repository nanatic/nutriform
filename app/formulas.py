"""
nutriform/formulas.py
Автор: …

В модуле собраны расчёты, необходимые бэкенду Nutriform:
* рекомендуемая масса (Lorentz, Broca/Brugsch);
* %-потери массы и риск нутриционных нарушений;
* площадь поверхности тела (Mosteller, Shuter–Aslani);
* индекс массы тела (+вариант для ампутаций) и его классификация;
* окружность талии и WHR;
* BMR (Mifflin-St Jeor, Harris–Benedict, Katch–McArdle);
* расчёты по биоимпедансометрии.
"""
from __future__ import annotations

import math
from enum import Enum
from typing import Optional


# ──────────────────────────────────────────────────────────────
# 1.  Рекомендуемая масса тела
# ──────────────────────────────────────────────────────────────
class Sex(str, Enum):
    MALE = "male"
    FEMALE = "female"


def lorentz_rec_weight(height_cm: float, sex: Sex) -> float:
    """Формула Lorentz (48/45 кг + …)."""
    delta = (height_cm - 152) * (1.1 if sex == Sex.MALE else 0.9)
    base = 48 if sex == Sex.MALE else 45
    return base + delta


def broca_brugsch_rec_weight(height_cm: float) -> float:
    """Брок (c поправкой Брюгша)."""
    if height_cm < 165:
        return height_cm - 100
    if height_cm <= 175:
        return height_cm - 105
    return height_cm - 110


# ──────────────────────────────────────────────────────────────
# 2.  Потеря массы тела и нутриционный риск
# ──────────────────────────────────────────────────────────────
def weight_loss_pct(initial_kg: float, current_kg: float) -> float:
    return (initial_kg - current_kg) / initial_kg * 100


def high_nutritional_risk(loss_pct: float, months: int) -> bool:
    limits = {1: 5, 3: 7.5, 6: 10}
    return loss_pct > limits.get(months, 10)


# ──────────────────────────────────────────────────────────────
# 3.  Площадь поверхности тела
# ──────────────────────────────────────────────────────────────
def bsa_mosteller(weight_kg: float, height_cm: float) -> float:
    return math.sqrt(weight_kg * height_cm / 3600)


def bsa_shuter(weight_kg: float, height_cm: float) -> float:
    return 0.00949 * weight_kg ** 0.441 * height_cm ** 0.655


# ──────────────────────────────────────────────────────────────
# 4.  Индекс массы тела
# ──────────────────────────────────────────────────────────────
_AMPUT_COEFF = {
    "whole_arm": 0.065, "upper_arm": 0.035, "hand": 0.008,
    "forearm_hand": 0.031, "whole_leg": 0.186, "foot": 0.018,
}


def bmi(weight_kg: float, height_cm: float) -> float:
    return 100 * weight_kg / height_cm ** 2


def bmi_with_amputation(weight_kg: float, height_m: float, coeff: float) -> float:
    base = weight_kg / height_m ** 2
    return base + coeff * base


def bmi_category(value: float) -> str:
    if value < 16:
        return "Выраженный дефицит"
    if value < 18.5:
        return "Недостаточная масса"
    if value < 25:
        return "Норма"
    if value < 30:
        return "Предожирение"
    if value < 35:
        return "Ожирение I"
    if value < 40:
        return "Ожирение II"
    return "Ожирение III"


# ──────────────────────────────────────────────────────────────
# 5.  Окружность талии и WHR
# ──────────────────────────────────────────────────────────────
def waist_status(waist_cm: float, sex: Sex) -> str:
    if sex == Sex.MALE:
        if waist_cm <= 94:
            return "Норма"
        if waist_cm <= 102:
            return "Профилактика набора веса"
        return "Коррекция массы"
    else:
        if waist_cm <= 80:
            return "Норма"
        if waist_cm <= 88:
            return "Профилактика набора веса"
        return "Коррекция массы"


def whr(waist_cm: float, hip_cm: float) -> float:
    return waist_cm / hip_cm


def whr_status(whr_val: float, sex: Sex) -> str:
    limit = 0.95 if sex == Sex.MALE else 0.8
    return "Абдоминальное ожирение" if whr_val > limit else "Оптимально"


# ──────────────────────────────────────────────────────────────
# 6.  BMR / Основной обмен
# ──────────────────────────────────────────────────────────────
def bmr_mifflin(weight_kg: float, height_cm: float, age: int, sex: Sex) -> float:
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    return base + (5 if sex == Sex.MALE else -161)


def bmr_harris(weight_kg: float, height_cm: float, age: int, sex: Sex) -> float:
    if sex == Sex.MALE:
        return 88.362 + 13.397 * weight_kg + 4.799 * height_cm - 5.677 * age
    return 447.593 + 9.247 * weight_kg + 3.098 * height_cm - 4.330 * age


def bmr_katch(ffm_kg: float) -> float:
    return 370 + 21.6 * ffm_kg


# ──────────────────────────────────────────────────────────────
# 7.  Биоимпедансометрия
# ──────────────────────────────────────────────────────────────
def fat_percent(fat_kg: float, weight_kg: float) -> float:
    return fat_kg / weight_kg * 100


def fat_mass_index(fat_kg: float, height_m: float) -> float:
    return fat_kg / height_m ** 2


def ffm_index(ffm_kg: float, height_m: float) -> float:
    return ffm_kg / height_m ** 2


def body_water_percent(total_water_kg: float, weight_kg: float) -> float:
    return total_water_kg / weight_kg * 100


def ecw_ratio(ecw_kg: float, total_water_kg: float) -> float:
    return ecw_kg / total_water_kg
