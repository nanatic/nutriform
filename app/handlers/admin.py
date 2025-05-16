from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.domain.models.profile_change_request import ProfileChangeRequestRead
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.admin_repository import AdminRepository
from app.use_cases.admin_use_cases import AdminService

router = APIRouter(prefix="/admin", tags=["Администрирование"])


def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    return AdminService(AdminRepository(db))


@router.get(
    "/profile-change-requests",
    response_model=List[ProfileChangeRequestRead],
    summary="Список заявок на изменение профиля"
)
def list_profile_change_requests(
        svc: AdminService = Depends(get_admin_service),
):
    return svc.list_requests()


@router.post(
    "/profile-change-requests/{request_id}/approve",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Одобрить заявку"
)
def approve_request(
        request_id: UUID,
        admin_id: UUID = Query(..., description="UUID администратора"),
        svc: AdminService = Depends(get_admin_service),
):
    try:
        svc.approve(request_id, admin_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Request not found")


@router.post(
    "/profile-change-requests/{request_id}/reject",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Отклонить заявку"
)
def reject_request(
        request_id: UUID,
        admin_id: UUID = Query(..., description="UUID администратора"),
        svc: AdminService = Depends(get_admin_service),
):
    try:
        svc.reject(request_id, admin_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Request not found")
