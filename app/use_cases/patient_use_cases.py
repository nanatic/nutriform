from app.domain.repositories.patient_repository_interface import AbstractPatientRepository
from app.domain.models.patient import PatientCreate, PatientRead

class PatientService:
    def __init__(self, repo: AbstractPatientRepository):
        self.repo = repo

    def create_patient(self, data: PatientCreate) -> int:
        # тут можно добавить валидацию
        return self.repo.create_patient(data)

    def get_patient(self, patient_id: int) -> PatientRead:
        patient = self.repo.get_by_id(patient_id)
        if not patient:
            raise ValueError("Patient not found")
        return patient

    def list_patients(self):
        return self.repo.list_all()