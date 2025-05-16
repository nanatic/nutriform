from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import uuid

class IBodyMetricsRepository(ABC):
    @abstractmethod
    def add_anthropometry(self, patient_id: int, data: Dict[str, Any]) -> uuid.UUID:
        ...

    @abstractmethod
    def get_latest_metrics(self, patient_id: int) -> Optional[Dict[str, Any]]:
        ...
