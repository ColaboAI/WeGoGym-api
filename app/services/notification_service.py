from uuid import UUID
from sqlalchemy import select, func

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification
from app.schemas.notification import (
    NotificationBase,
    NotificationRead,
    NotificationUpdate,
)

from sqlalchemy.orm import selectinload


async def get_notification_list(
    db: AsyncSession,
    user_id: UUID,
    limit: int = 10,
    offset: int | None = 0,
) -> tuple[int | None, list[Notification]]:
    async with db.begin():
        stmt = (
            select(Notification)
            .order_by(Notification.created_at.desc())
            .options(selectinload(Notification.recipient))
            .where(Notification.recipient_id == user_id)
            .offset(offset)
            .limit(limit)
        )
        t_stmt = (
            select(func.count("*"))
            .where(Notification.recipient_id == user_id)
            .select_from(Notification)
        )

        total = await db.execute(t_stmt)
        result = await db.execute(stmt)

        return total.scalar(), result.scalars().all()


# async def create_notification(
#     session: AsyncSession,
#     notification: NotificationBase,
# ) -> NotificationRead:
#     """
#     알림 정보를 생성합니다.
#     """
#     notification = Notification(**notification.dict())
#     session.add(notification)
#     await session.commit()
#     return notification
