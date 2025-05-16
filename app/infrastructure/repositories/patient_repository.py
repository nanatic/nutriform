import random
from typing import Optional, List
from sqlalchemy.orm import Session
from app.domain.models.patient import PatientCreate, PatientRead
from app.domain.repositories.patient_repository_interface import AbstractPatientRepository
from app.infrastructure.db.models import Patients

class PatientRepository(AbstractPatientRepository):
    def __init__(self, session: Session):
        self.session = session

    def generate_unique_patient_id(self) -> int:
        while True:
            new_id = random.randint(100000, 9999999)
            if not self.session.query(Patients).get(new_id):
                return new_id

    def create_patient(self, data: PatientCreate) -> int:
        new_id = self.generate_unique_patient_id()
        patient = Patients(
            id=new_id,
            full_name=data.full_name,
            birth_date=data.birth_date,
            place_of_residence=data.place_of_residence
        )
        self.session.add(patient)
        self.session.commit()
        return new_id

    def get_by_id(self, patient_id: int) -> Optional[PatientRead]:
        p = self.session.query(Patients).get(patient_id)
        if not p: return None
        return PatientRead(**p.__dict__)

    def list_all(self) -> List[PatientRead]:
        xs = self.session.query(Patients).all()
        return [PatientRead(**x.__dict__) for x in xs]
