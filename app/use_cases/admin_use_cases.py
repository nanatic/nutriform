from typing import List
from uuid import UUID

from app.domain.models.profile_change_request import ProfileChangeRequestRead
from app.domain.repositories.admin_repository_interface import IAdminRepository


class AdminService:
    def __init__(self, repo: IAdminRepository):
        self.repo = repo

    def list_requests(self) -> List[ProfileChangeRequestRead]:
        raw = self.repo.list_requests()
        return [ProfileChangeRequestRead(**r.__dict__) for r in raw]

    def approve(self, request_id: UUID, admin_id: UUID) -> None:
        req = self.repo.update_request_status(request_id, 'approved', admin_id)
        msg = f"Ваша заявка {request_id} одобрена администратором"
        self.repo.create_notification(req.user_id, msg)

    def reject(self, request_id: UUID, admin_id: UUID) -> None:
        req = self.repo.update_request_status(request_id, 'rejected', admin_id)
        msg = f"Ваша заявка {request_id} отклонена администратором"
        self.repo.create_notification(req.user_id, msg)
