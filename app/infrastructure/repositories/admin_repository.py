from typing import Type
from uuid import UUID

from sqlalchemy.orm import Session

from app.infrastructure.db.models import ProfileChangeRequests, Notifications
from app.domain.repositories.admin_repository_interface import IAdminRepository

class AdminRepository(IAdminRepository):
    def __init__(self, session: Session):
        self.session = session

    def list_requests(self) -> list[Type[ProfileChangeRequests]]:
        return (
            self.session
            .query(ProfileChangeRequests)
            .order_by(ProfileChangeRequests.submitted_at.desc())
            .all()
        )

    def update_request_status(
            self, request_id: UUID, status: str, admin_id: UUID
    ) -> ProfileChangeRequests:
        req = self.session.get(ProfileChangeRequests, request_id)
        if not req:
            raise ValueError("Request not found")
        req.status = status
        req.reviewed_by = admin_id
        self.session.commit()
        return req

    def create_notification(self, user_id: UUID, message: str) -> int:
        notif = Notifications(user_id=user_id, message=message)
        self.session.add(notif)
        self.session.commit()
        return notif.id
