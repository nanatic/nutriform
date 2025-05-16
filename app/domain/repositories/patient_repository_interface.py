from abc import ABC, abstractmethod
from typing import Optional, List
from ..models.patient import PatientCreate, PatientRead

class AbstractPatientRepository(ABC):
    @abstractmethod
    def create_patient(self, data: PatientCreate) -> int:
        ...

    @abstractmethod
    def get_by_id(self, patient_id: int) -> Optional[PatientRead]:
        ...

    @abstractmethod
    def list_all(self) -> List[PatientRead]:
        ...