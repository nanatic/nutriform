import uuid
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class IBodyMetricsRepository(ABC):
    @abstractmethod
    def add_anthropometry(
            self, patient_id: int, data: Dict[str, Any]
    ) -> uuid.UUID:
        """Соз-даёт запись в anthropometries + расчётные показатели в body_metrics.
        Возвращает ID новой записи (UUID)."""
        ...

    @abstractmethod
    def get_latest_metrics(
            self, patient_id: int
    ) -> Optional[Dict[str, Any]]:
        """Возвращает последнюю запись с объединёнными данными
        (anthropometries ⊕ body_metrics) или None."""
        ...
