from uuid import UUID
from fastapi import APIRouter, Body, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import UnauthorizedException
from app.core.fastapi.dependencies.premission import (
    IsAuthenticated,
    PermissionDependency,
)

from app.schemas.notification import (
    NotificationWorkoutBase,
    NotificationWorkoutRead,
    NotificationWorkoutListResponse,
)

from app.services.notification_service import (
    get_notification_workout_list,
)
from app.session import get_db_transactional_session

notification_router = APIRouter()


# 운동 알림 정보 조회 엔드포인트
@notification_router.get(
    "/workout",
    response_model=NotificationWorkoutListResponse,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def get_notifications_workout(
    req: Request,
    session: AsyncSession = Depends(get_db_transactional_session),
    limit: int = Query(10, description="Limit"),
    offset: int = Query(0, description="offset"),
):
    total, n_list = await get_notification_workout_list(
        session, req.user.id, limit, offset
    )

    return {
        "total": total,
        "items": n_list,
        "next_cursor": offset + len(n_list)
        if total and total > offset + len(n_list)
        else None,
    }
