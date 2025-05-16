from typing import Optional
from app.domain.repositories.body_metrics_repository_interface import IBodyMetricsRepository
from app.domain.models.anthropometry import AnthropometryCreate, AnthropometryRead

class BodyMetricsService:
    def __init__(self, repo: IBodyMetricsRepository):
        self.repo = repo

    def add_anthropometry(self, patient_id: int, data: AnthropometryCreate) -> str:
        return str(self.repo.add_anthropometry(patient_id, data.dict()))

    def get_latest(self, patient_id: int) -> Optional[AnthropometryRead]:
        raw = self.repo.get_latest_metrics(patient_id)
        return AnthropometryRead(**raw) if raw else None