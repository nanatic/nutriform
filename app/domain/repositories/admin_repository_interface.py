from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from app.infrastructure.db.models import ProfileChangeRequests


class IAdminRepository(ABC):
    @abstractmethod
    def list_requests(self) -> List[ProfileChangeRequests]: ...

    @abstractmethod
    def update_request_status(
        self, request_id: UUID, status: str, admin_id: UUID
    ) -> ProfileChangeRequests: ...

    @abstractmethod
    def create_notification(self, user_id: UUID, message: str) -> int: ...
