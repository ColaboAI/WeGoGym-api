from uuid import UUID
from fastapi import APIRouter, Body, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import UnauthorizedException
from app.core.fastapi.dependencies.premission import (
    IsAuthenticated,
    PermissionDependency,
)

from app.schemas.notification import (
    NotificationBase,
    NotificationRead,
    NotificationUpdate,
    NotificationListResponse,
)

from app.services.notification_service import (
    get_notification_list,
)
from app.session import get_db_transactional_session

notification_router = APIRouter()


# 알림 정보 조회 엔드포인트
@notification_router.get(
    "",
    response_model=NotificationListResponse,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def get_notifications(
    session: AsyncSession = Depends(get_db_transactional_session),
    limit: int = Query(10, description="Limit"),
    offset: int = Query(0, description="offset"),
):
    total, n_list = await get_notification_list(session, limit, offset)

    return {
        "total": total,
        "items": n_list,
        "next_cursor": offset + len(n_list)
        if total and total > offset + len(n_list)
        else None,
    }


# 알림 정보 생성 엔드포인트
@notification_router.post(
    "",
    response_model=NotificationRead,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def create_notification(
    notification: NotificationBase,
    session: AsyncSession = Depends(get_db_transactional_session),
):
    return await create_notification(session, notification)


# 알림 정보 수정 엔드포인트
@notification_router.put(
    "/{notification_id}",
    response_model=NotificationRead,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def update_notification_by_id(
    notification_id: UUID,
    notification: NotificationUpdate,
    session: AsyncSession = Depends(get_db_transactional_session),
):
    return await update_notification_by_id(session, notification_id, notification)
