import datetime
import uuid
from typing import Dict, Any, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.models.patient import PatientRead
from app.domain.models.users import UserUpdate, ProfileChangeRequestCreate
from app.domain.repositories.user_repository_interface import IUserRepository
from app.infrastructure.db.models import (
    Users, ProfileChangeRequests, PatientUserLinks, Patients,
    Anthropometries, QuestionnaireSubmissions
)


class UserRepository(IUserRepository):
    def __init__(self, session: Session):
        self.session = session

    # --------------------------------------------------
    # 1.‑‑2.  (обновление профиля)
    def update_user_info(self, user_id: str, new_data: UserUpdate) -> None:
        user = self.session.get(Users, user_id)
        if not user:
            raise ValueError("User not found")

        if new_data.email:
            exists = (self.session.query(Users)
                      .filter(Users.email == new_data.email,
                              Users.id != user_id)
                      .first())
            if exists:
                raise ValueError("Email already in use")

        for field, value in new_data:
            if value is not None:
                setattr(user, field, value)

        self.session.commit()

    def create_profile_change_request(
        self, user_id: str, request: ProfileChangeRequestCreate
    ) -> str:
        req = ProfileChangeRequests(
            id=uuid.uuid4(),
            user_id=user_id,
            requested_fields=request.requested_fields,
            status='pending',
            submitted_at=datetime.datetime.utcnow()
        )
        self.session.add(req)
        self.session.commit()
        return str(req.id)

    # --------------------------------------------------
    # 5‑‑8.  операции доктора
    # проверять, что user.role == 'doctor', можно выше – в сервисе/эндпойнте
    def add_patient_link(self, doctor_id: str, patient_id: int) -> None:
        link = self.session.get(PatientUserLinks, (doctor_id, patient_id))
        if link:
            link.status = 'active'
        else:
            link = PatientUserLinks(
                user_id=doctor_id,
                patient_id=patient_id,
                added_at=datetime.datetime.utcnow(),
                status='active'
            )
            self.session.add(link)
        self.session.commit()

    def deactivate_patient_link(self, doctor_id: str, patient_id: int) -> None:
        link = self.session.get(PatientUserLinks, (doctor_id, patient_id))
        if not link:
            raise ValueError("Link not found")
        link.status = 'inactive'
        self.session.commit()

    def _base_query(self, doctor_id: str):
        return (self.session.query(Patients)
                .join(PatientUserLinks,
                      (PatientUserLinks.patient_id == Patients.id)
                      & (PatientUserLinks.user_id == doctor_id)
                      & (PatientUserLinks.status == 'active')))

    def list_patients(self, doctor_id: str) -> List[PatientRead]:
        patients = self._base_query(doctor_id).all()
        return [PatientRead(**p.__dict__) for p in patients]

    def search_patients(self, doctor_id: str, filters: Dict[str, Any]) -> List[PatientRead]:
        q = self._base_query(doctor_id)
        if name := filters.get("full_name"):
            q = q.filter(Patients.full_name.ilike(f"%{name}%"))
        if bd := filters.get("birth_date"):
            q = q.filter(Patients.birth_date == bd)
        return [PatientRead(**p.__dict__) for p in q.all()]

    def get_patient_stats(self, doctor_id: str, all_patients: bool=False) -> Dict[str, Any]:
        if all_patients:
            Sub = Patients.__table__
        else:
            Sub = self._base_query(doctor_id).subquery()

        count = self.session.query(func.count()).select_from(Sub).scalar()
        avg_age = self.session.query(
            func.avg(func.date_part('year', func.age(func.current_date(), Sub.c.birth_date)))
        ).scalar()

        avg_bmi = (self.session.query(func.avg(Anthropometries.bmi))
                   .join(Sub, Anthropometries.patient_id == Sub.c.id)
                   .scalar())

        surveys = (self.session.query(func.count(QuestionnaireSubmissions.id))
                   .join(Sub, QuestionnaireSubmissions.patient_id == Sub.c.id)
                   .scalar())

        return {
            "total_patients": count or 0,
            "average_age": avg_age,
            "average_bmi": avg_bmi,
            "total_surveys": surveys or 0
        }
