from abc import ABC, abstractmethod
from typing import Dict, Any, List
from uuid import UUID

from app.domain.models.patient import PatientRead
from app.domain.models.users import UserUpdate, ProfileChangeRequestCreate


class IUserRepository(ABC):
    # --- обычные операции пользователя ---
    @abstractmethod
    def update_user_info(self, user_id: str, new_data: UserUpdate) -> None: ...

    @abstractmethod
    def create_profile_change_request(self, user_id: str,
                                      request: ProfileChangeRequestCreate) -> str: ...

    @abstractmethod
    def list_notifications(self, user_id: UUID) -> list[dict]: ...

    # --- «докторские» операции ---
    @abstractmethod
    def add_patient_link(self, doctor_id: str, patient_id: int) -> None: ...

    @abstractmethod
    def deactivate_patient_link(self, doctor_id: str, patient_id: int) -> None: ...

    @abstractmethod
    def list_patients(self, doctor_id: str) -> List[PatientRead]: ...

    @abstractmethod
    def search_patients(self, doctor_id: str, filters: Dict[str, Any]) -> List[PatientRead]: ...

    @abstractmethod
    def get_patient_stats(self, doctor_id: str, all_patients: bool = False) -> Dict[str, Any]: ...
