from typing import Dict, Any, List
from app.domain.repositories.user_repository_interface import IUserRepository
from app.domain.models.users import UserUpdate, ProfileChangeRequestCreate, NotificationRead
from app.domain.models.patient import PatientRead


class UserService:
    def __init__(self, repo: IUserRepository):
        self.repo = repo

    # ==== «обычные» операции ====
    def edit_profile(self, user_id: str, data: UserUpdate):
        self.repo.update_user_info(user_id, data)

    def request_profile_change(self, user_id: str, data: ProfileChangeRequestCreate):
        return self.repo.create_profile_change_request(user_id, data)

    # ==== «докторские» операции ====
    def add_patient(self, doctor_id: str, patient_id: int):
        self.repo.add_patient_link(doctor_id, patient_id)

    def remove_patient(self, doctor_id: str, patient_id: int):
        self.repo.deactivate_patient_link(doctor_id, patient_id)

    def list_patients(self, doctor_id: str) -> List[PatientRead]:
        return self.repo.list_patients(doctor_id)

    def search_patients(self, doctor_id: str, filters: Dict[str, Any]):
        return self.repo.search_patients(doctor_id, filters)

    def stats(self, doctor_id: str, all_patients: bool=False) -> Dict[str, Any]:
        return self.repo.get_patient_stats(doctor_id, all_patients)

    def get_notifications(self, user_id: str) -> list[NotificationRead]:
        data = self.repo.list_notifications(user_id)
        return [NotificationRead(**n) for n in data]
