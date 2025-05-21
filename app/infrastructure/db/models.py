import datetime
import decimal
import uuid
from typing import List, Optional

from sqlalchemy import ARRAY, BigInteger, CheckConstraint, Date, DateTime, Double, Enum, ForeignKeyConstraint, Integer, \
    Numeric, PrimaryKeyConstraint, Sequence, String, Text, Time, UniqueConstraint, Uuid, text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Anthropometries(Base):
    __tablename__ = "anthropometries"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="anthropometries_pkey"),
        ForeignKeyConstraint(
            ["patient_id"],
            ["patients.id"],
            ondelete="CASCADE",
            name="anthropometries_patient_id_fkey",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    height_cm: Mapped[float] = mapped_column(Double)
    weight_kg: Mapped[float] = mapped_column(Double)
    measured_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    patient_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    waist_cm: Mapped[Optional[float]] = mapped_column(Double)
    hip_cm: Mapped[Optional[float]] = mapped_column(Double)

    patient: Mapped["Patients"] = relationship(
        "Patients", back_populates="anthropometries"
    )

    body_metrics: Mapped[Optional["BodyMetrics"]] = relationship(
        "BodyMetrics",
        back_populates="anthropometry",
        uselist=False,
        cascade="all, delete-orphan"
    )


class BodyMetrics(Base):
    __tablename__ = "body_metrics"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="body_metrics_pkey"),
        UniqueConstraint(
            "anthropometry_id", name="unq_body_metrics_anthropometry_id"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    anthropometry_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("anthropometries.id", ondelete="CASCADE"),
        nullable=False,
    )

    bmi: Mapped[Optional[float]] = mapped_column(Double)
    bsa: Mapped[Optional[float]] = mapped_column(Double)
    ideal_weight: Mapped[Optional[float]] = mapped_column(Double)
    bmr: Mapped[Optional[float]] = mapped_column(Double)
    method_bmr: Mapped[Optional[str]] = mapped_column(Text)
    method_bsa: Mapped[Optional[str]] = mapped_column(Text)

    anthropometry: Mapped["Anthropometries"] = relationship(
        "Anthropometries",
        back_populates="body_metrics",
        uselist=False
    )


class FoodGroups(Base):
    __tablename__ = 'food_groups'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='food_groups_pkey'),
        UniqueConstraint('name', name='food_groups_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)

    food_composition: Mapped[List['FoodComposition']] = relationship('FoodComposition', back_populates='group')
    questionnaire_questions: Mapped[List['QuestionnaireQuestions']] = relationship('QuestionnaireQuestions',
                                                                                   back_populates='food_group')


class FoodLogEntries(Base):
    __tablename__ = 'food_log_entries'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='food_log_entries_pkey'),
        UniqueConstraint('food_item_id', name='unq_food_log_entries_food_item_id'),
        UniqueConstraint('food_log_id', name='unq_food_log_entries_food_log_id')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    food_log_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    food_item_id: Mapped[Optional[int]] = mapped_column(Integer)
    portion_grams: Mapped[Optional[float]] = mapped_column(Double(53))
    meal_time: Mapped[Optional[datetime.time]] = mapped_column(Time)
    notes: Mapped[Optional[str]] = mapped_column(Text)


class Patients(Base):
    __tablename__ = 'patients'
    __table_args__ = (
        CheckConstraint("sex = ANY (ARRAY['male'::text, 'female'::text])", name='patients_sex_check'),
        PrimaryKeyConstraint('id', name='patients_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, Sequence('patient_id_seq'), primary_key=True)
    full_name: Mapped[str] = mapped_column(Text)
    birth_date: Mapped[datetime.date] = mapped_column(Date)
    sex: Mapped[str] = mapped_column(Text)
    place_of_residence: Mapped[Optional[str]] = mapped_column(Text)

    anthropometries: Mapped[List['Anthropometries']] = relationship('Anthropometries', back_populates='patient')
    bioimpedance_samples: Mapped[List['BioimpedanceSamples']] = relationship('BioimpedanceSamples',
                                                                             back_populates='patient')
    clinical_histories: Mapped[List['ClinicalHistories']] = relationship('ClinicalHistories', back_populates='patient')
    dietary_histories: Mapped[List['DietaryHistories']] = relationship('DietaryHistories', back_populates='patient')
    food_logs: Mapped[List['FoodLogs']] = relationship('FoodLogs', back_populates='patient')
    meal_plans: Mapped[List['MealPlans']] = relationship('MealPlans', back_populates='patient')
    patient_user_links: Mapped[List['PatientUserLinks']] = relationship('PatientUserLinks', back_populates='patient')
    questionnaire_submissions: Mapped[List['QuestionnaireSubmissions']] = relationship('QuestionnaireSubmissions',
                                                                                       back_populates='patient')


class Questionnaires(Base):
    __tablename__ = 'questionnaires'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='questionnaires_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    type: Mapped[Optional[str]] = mapped_column(Enum('nutrition', 'physical_activity', name='questionnaire_type'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    questionnaire_questions: Mapped[List['QuestionnaireQuestions']] = relationship('QuestionnaireQuestions',
                                                                                   back_populates='questionnaire')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        CheckConstraint("role = ANY (ARRAY['doctor'::text, 'admin'::text])", name='users_role_check'),
        PrimaryKeyConstraint('id', name='users_pkey'),
        UniqueConstraint('email', name='users_email_key'),
        UniqueConstraint('oidc_sub', name='users_oidc_sub_key')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    email: Mapped[str] = mapped_column(Text)
    full_name: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(Text)
    oidc_sub: Mapped[str] = mapped_column(Text)
    position: Mapped[Optional[str]] = mapped_column(Text)

    patient_user_links: Mapped[List['PatientUserLinks']] = relationship('PatientUserLinks', back_populates='user')
    profile_change_requests: Mapped[List['ProfileChangeRequests']] = relationship('ProfileChangeRequests',
                                                                                  foreign_keys='[ProfileChangeRequests.reviewed_by]',
                                                                                  back_populates='users')
    profile_change_requests_: Mapped[List['ProfileChangeRequests']] = relationship('ProfileChangeRequests',
                                                                                   foreign_keys='[ProfileChangeRequests.user_id]',
                                                                                   back_populates='user')
    notifications: Mapped[List['Notifications']] = relationship('Notifications', back_populates='user')


class BioimpedanceSamples(Base):
    __tablename__ = 'bioimpedance_samples'
    __table_args__ = (
        ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE',
                             name='bioimpedance_samples_patient_id_fkey'),
        PrimaryKeyConstraint('id', name='bioimpedance_samples_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    measured_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    patient_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    fat_mass_kg: Mapped[Optional[float]] = mapped_column(Double(53))
    lean_mass_kg: Mapped[Optional[float]] = mapped_column(Double(53))
    total_body_water_l: Mapped[Optional[float]] = mapped_column(Double(53))
    bcm: Mapped[Optional[float]] = mapped_column(Double(53))
    phase_angle: Mapped[Optional[float]] = mapped_column(Double(53))

    patient: Mapped[Optional['Patients']] = relationship('Patients', back_populates='bioimpedance_samples')


class ClinicalHistories(Base):
    __tablename__ = 'clinical_histories'
    __table_args__ = (
        ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE',
                             name='clinical_histories_patient_id_fkey'),
        PrimaryKeyConstraint('id', name='clinical_histories_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    patient_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    chronic_diseases: Mapped[Optional[list]] = mapped_column(ARRAY(Text()))
    medications: Mapped[Optional[list]] = mapped_column(ARRAY(Text()))
    physical_activity: Mapped[Optional[dict]] = mapped_column(JSONB)

    patient: Mapped[Optional['Patients']] = relationship('Patients', back_populates='clinical_histories')


class DietaryHistories(Base):
    __tablename__ = 'dietary_histories'
    __table_args__ = (
        ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE',
                             name='dietary_histories_patient_id_fkey'),
        PrimaryKeyConstraint('id', name='dietary_histories_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    patient_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    ffq_responses: Mapped[Optional[dict]] = mapped_column(JSONB)
    allergies: Mapped[Optional[list]] = mapped_column(ARRAY(Text()))
    food_preferences: Mapped[Optional[dict]] = mapped_column(JSONB)

    patient: Mapped[Optional['Patients']] = relationship('Patients', back_populates='dietary_histories')


class FoodComposition(Base):
    __tablename__ = 'food_composition'
    __table_args__ = (
        ForeignKeyConstraint(['group_id'], ['food_groups.id'], ondelete='CASCADE',
                             name='food_composition_group_id_fkey'),
        PrimaryKeyConstraint('id', name='food_composition_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(Integer)
    product_code: Mapped[str] = mapped_column(Text)
    product_name: Mapped[str] = mapped_column(Text)
    water_percent: Mapped[Optional[float]] = mapped_column(Double(53))
    protein_percent: Mapped[Optional[float]] = mapped_column(Double(53))
    fat_percent: Mapped[Optional[float]] = mapped_column(Double(53))
    nzhk_mg_percent: Mapped[Optional[float]] = mapped_column(Double(53))
    cholesterol_mg_percent: Mapped[Optional[float]] = mapped_column(Double(53))
    mds_percent: Mapped[Optional[float]] = mapped_column(Double(53))
    starch_percent: Mapped[Optional[float]] = mapped_column(Double(53))
    carbohydrate_percent: Mapped[Optional[float]] = mapped_column(Double(53))
    fiber_percent: Mapped[Optional[float]] = mapped_column(Double(53))
    organic_acids_percent: Mapped[Optional[float]] = mapped_column(Double(53))
    ash_percent: Mapped[Optional[float]] = mapped_column(Double(53))
    sodium_mg_percent: Mapped[Optional[float]] = mapped_column(Double(53))
    potassium_mg_percent: Mapped[Optional[float]] = mapped_column(Double(53))
    calcium_mg_percent: Mapped[Optional[float]] = mapped_column(Double(53))
    magnesium_mg_percent: Mapped[Optional[float]] = mapped_column(Double(53))
    phosphorus_mg_percent: Mapped[Optional[float]] = mapped_column(Double(53))
    iron_mg_percent: Mapped[Optional[float]] = mapped_column(Double(53))
    retinol_mcg_percent: Mapped[Optional[float]] = mapped_column(Double(53))
    carotene_mcg_percent: Mapped[Optional[float]] = mapped_column(Double(53))
    retinol_equiv_mcg: Mapped[Optional[float]] = mapped_column(Double(53))
    tocopherol_mg_percent: Mapped[Optional[float]] = mapped_column(Double(53))
    thiamine_mg: Mapped[Optional[float]] = mapped_column(Double(53))
    riboflavin_mg: Mapped[Optional[float]] = mapped_column(Double(53))
    niacin_mg: Mapped[Optional[float]] = mapped_column(Double(53))
    niacin_equiv_mg: Mapped[Optional[float]] = mapped_column(Double(53))
    ascorbic_acid_mg: Mapped[Optional[float]] = mapped_column(Double(53))
    calories_kcal: Mapped[Optional[float]] = mapped_column(Double(53))
    portion_grams: Mapped[Optional[float]] = mapped_column(Double(53))
    polyunsat_fat_percent: Mapped[Optional[float]] = mapped_column(Double(53))
    alcohol_by_weight_percent: Mapped[Optional[float]] = mapped_column(Double(53))

    group: Mapped['FoodGroups'] = relationship('FoodGroups', back_populates='food_composition')


class FoodLogs(FoodLogEntries):
    __tablename__ = 'food_logs'
    __table_args__ = (
        ForeignKeyConstraint(['id'], ['food_log_entries.food_log_id'], name='fk_food_logs_food_log_entries'),
        ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE', name='food_logs_patient_id_fkey'),
        PrimaryKeyConstraint('id', name='food_logs_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    logged_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    patient_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    days_covered: Mapped[Optional[int]] = mapped_column(Integer)

    patient: Mapped[Optional['Patients']] = relationship('Patients', back_populates='food_logs')


class MealPlans(Base):
    __tablename__ = 'meal_plans'
    __table_args__ = (
        ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE', name='meal_plans_patient_id_fkey'),
        PrimaryKeyConstraint('id', name='meal_plans_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    generated_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    patient_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    constraints_applied: Mapped[Optional[dict]] = mapped_column(JSONB)

    patient: Mapped[Optional['Patients']] = relationship('Patients', back_populates='meal_plans')
    day_menus: Mapped[List['DayMenus']] = relationship('DayMenus', back_populates='meal_plan')


class PatientUserLinks(Base):
    __tablename__ = 'patient_user_links'
    __table_args__ = (
        CheckConstraint("status = ANY (ARRAY['active'::text, 'inactive'::text])",
                        name='patient_user_links_status_check'),
        ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE',
                             name='patient_user_links_patient_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='patient_user_links_user_id_fkey'),
        PrimaryKeyConstraint('user_id', 'patient_id', name='patient_user_links_pkey')
    )

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    patient_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    added_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(Text, server_default=text("'active'::text"))

    patient: Mapped['Patients'] = relationship('Patients', back_populates='patient_user_links')
    user: Mapped['Users'] = relationship('Users', back_populates='patient_user_links')


class ProfileChangeRequests(Base):
    __tablename__ = 'profile_change_requests'
    __table_args__ = (
        CheckConstraint("status = ANY (ARRAY['pending'::text, 'approved'::text, 'rejected'::text])",
                        name='profile_change_requests_status_check'),
        ForeignKeyConstraint(['reviewed_by'], ['users.id'], name='profile_change_requests_reviewed_by_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE',
                             name='profile_change_requests_user_id_fkey'),
        PrimaryKeyConstraint('id', name='profile_change_requests_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    submitted_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(Text)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    requested_fields: Mapped[Optional[dict]] = mapped_column(JSONB)
    reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    users: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[reviewed_by],
                                                    back_populates='profile_change_requests')
    user: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[user_id],
                                                   back_populates='profile_change_requests_')


class QuestionnaireQuestions(Base):
    __tablename__ = 'questionnaire_questions'
    __table_args__ = (
        ForeignKeyConstraint(['food_group_id'], ['food_groups.id'], ondelete='SET NULL',
                             name='questionnaire_questions_food_group_id_fkey'),
        ForeignKeyConstraint(['questionnaire_id'], ['questionnaires.id'], ondelete='CASCADE',
                             name='questionnaire_questions_questionnaire_id_fkey'),
        PrimaryKeyConstraint('id', name='questionnaire_questions_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    questionnaire_id: Mapped[int] = mapped_column(Integer)
    question_text: Mapped[str] = mapped_column(Text)
    question_order: Mapped[Optional[int]] = mapped_column(Integer)
    answers_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    food_group_id: Mapped[Optional[int]] = mapped_column(Integer)
    portion_description: Mapped[Optional[str]] = mapped_column(Text)

    food_group: Mapped[Optional['FoodGroups']] = relationship('FoodGroups', back_populates='questionnaire_questions')
    questionnaire: Mapped['Questionnaires'] = relationship('Questionnaires', back_populates='questionnaire_questions')
    questionnaire_answers: Mapped[List['QuestionnaireAnswers']] = relationship('QuestionnaireAnswers',
                                                                               back_populates='question')


class QuestionnaireSubmissions(Base):
    __tablename__ = 'questionnaire_submissions'
    __table_args__ = (
        ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE',
                             name='questionnaire_submissions_patient_id_fkey'),
        PrimaryKeyConstraint('id', name='questionnaire_submissions_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    questionnaire_type: Mapped[str] = mapped_column(Text)
    submitted_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    patient_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    responses: Mapped[Optional[dict]] = mapped_column(JSONB)
    total_met_minutes: Mapped[Optional[float]] = mapped_column(Double)

    patient: Mapped[Optional['Patients']] = relationship('Patients', back_populates='questionnaire_submissions')
    questionnaire_answers: Mapped[List['QuestionnaireAnswers']] = relationship('QuestionnaireAnswers',
                                                                               back_populates='submission')


class DayMenus(Base):
    __tablename__ = 'day_menus'
    __table_args__ = (
        ForeignKeyConstraint(['meal_plan_id'], ['meal_plans.id'], name='fk_day_menus_meal_plans'),
        PrimaryKeyConstraint('id', name='day_menus_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    day_number: Mapped[int] = mapped_column(Integer)
    meal_plan_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    total_calories: Mapped[Optional[float]] = mapped_column(Double(53))

    meal_plan: Mapped[Optional['MealPlans']] = relationship('MealPlans', back_populates='day_menus')
    meals: Mapped[List['Meals']] = relationship('Meals', back_populates='day_menu')


class QuestionnaireAnswers(Base):
    __tablename__ = 'questionnaire_answers'
    __table_args__ = (
        ForeignKeyConstraint(['question_id'], ['questionnaire_questions.id'],
                             name='fk_questionnaire_answers_questionnaire_questions'),
        ForeignKeyConstraint(['submission_id'], ['questionnaire_submissions.id'], ondelete='CASCADE',
                             name='questionnaire_answers_submission_id_fkey'),
        PrimaryKeyConstraint('id', name='questionnaire_answers_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    submission_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    question_id: Mapped[Optional[int]] = mapped_column(Integer)
    frequency_eat: Mapped[Optional[str]] = mapped_column(
        Enum('never', '1-3 per month', '1 per week', '2-4 per week', '1 per day', '2-3 per day', '4+ per day',
             name='frequency_type'))
    recorded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    days_per_week: Mapped[Optional[int]] = mapped_column(Integer)
    met_minutes: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2))

    question: Mapped[Optional['QuestionnaireQuestions']] = relationship('QuestionnaireQuestions',
                                                                        back_populates='questionnaire_answers')
    submission: Mapped[Optional['QuestionnaireSubmissions']] = relationship('QuestionnaireSubmissions',
                                                                            back_populates='questionnaire_answers')


class Meals(Base):
    __tablename__ = 'meals'
    __table_args__ = (
        ForeignKeyConstraint(['day_menu_id'], ['day_menus.id'], ondelete='CASCADE', name='meals_day_menu_id_fkey'),
        PrimaryKeyConstraint('id', name='meals_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    day_menu_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    name: Mapped[Optional[str]] = mapped_column(Text)
    items: Mapped[Optional[dict]] = mapped_column(JSONB)
    time: Mapped[Optional[datetime.time]] = mapped_column(Time)

    day_menu: Mapped[Optional['DayMenus']] = relationship('DayMenus', back_populates='meals')


class Notifications(Base):
    __tablename__ = 'notifications'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey('users.id', ondelete='CASCADE'), nullable=False
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=text('CURRENT_TIMESTAMP'), nullable=False
    )
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user = relationship('Users', back_populates='notifications')
