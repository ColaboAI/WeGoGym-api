from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy import select, func

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions.notification import (
    NotAdminOfNotificationException,
    NotificaitonNotFoundException,
)
from app.models.notification import NotificationWorkout, Notification
from app.models.workout_promise import WorkoutParticipant, WorkoutPromise
from app.schemas.notification import (
    NotificationWorkoutBase,
)

from sqlalchemy.orm import selectinload
from app.services.user_service import get_my_info_by_id
from app.services.workout_promise_service import (
    get_workout_participant_id_list_by_user_id,
)


# 내 운동 알림 정보 조회
async def get_notification_workout_list(
    db: AsyncSession,
    user_id: UUID,
    limit: int = 10,
    offset: int | None = 0,
) -> tuple[int | None, list[NotificationWorkout]]:
    workout_participant_id_list_by_user_id = (
        await get_workout_participant_id_list_by_user_id(db, user_id)
    )

    stmt = (
        select(NotificationWorkout)
        .order_by(NotificationWorkout.created_at.desc())
        .options(
            selectinload(NotificationWorkout.sender).options(
                selectinload(WorkoutParticipant.user).load_only(
                    "id", "username", "profile_pic"
                )
            ),
            selectinload(NotificationWorkout.recipient).options(
                selectinload(WorkoutParticipant.user)
            ),
        )
        .where(
            NotificationWorkout.recipient_id.in_(workout_participant_id_list_by_user_id)
        )
    )

    t_stmt = (
        select(func.count("*"))
        .where(
            NotificationWorkout.recipient_id.in_(workout_participant_id_list_by_user_id)
        )
        .select_from(NotificationWorkout)
    )

    if offset:
        stmt = stmt.offset(offset)

    if limit:
        stmt = stmt.limit(limit)

    total = await db.execute(t_stmt)
    result = await db.execute(stmt)

    return total.scalars().first(), result.scalars().all()


async def update_notification_workout_by_id(
    db: AsyncSession,
    user_id: UUID,
    notification_id: UUID,
) -> NotificationWorkout:
    stmt = select(Notification).where(Notification.id == notification_id)
    res = await db.execute(stmt)
    notification = res.scalars().first()
    if not notification:
        raise NotificaitonNotFoundException()

    notification.read_at = datetime.now(timezone.utc)

    await db.commit()

    return notification


# 새로운 운동 약속 참가자 알림 생성
# 보내는 사람 : 운동 약속 생성자
# 받는 사람 : 운동 약속 생성자와 새로운 참가자 제외 -> 기존의 참가자들
# 알림 발생 시점 : 운동 약속 생성자가 새로운 참가자의 요청을 수락할 때
# async def create_notification_workout_new_participant(
#     db: AsyncSession,
#     # 운동 약속 생성자
#     admin_user_id: UUID,
#     # 새로운 참가자
#     new_participant_user_id: UUID,
#     workout_promise: WorkoutPromise,
#     notification: NotificationWorkoutBase,
# ) -> None:
#     async with db.begin():
#         sender = await get_my_info_by_id(admin_user_id, db)
#         participants = workout_promise.participants

#         for participant in participants:
#             # 운동 약속 생성자와 새로운 참가자 제외
#             if (
#                 participant.user_id == admin_user_id
#                 or participant.user_id == new_participant_user_id
#             ):
#                 continue
#             new_notification = NotificationWorkout(
#                 **notification.dict(),
#                 sender_id=admin_user_id,
#                 recipient_id=participant.id,
#                 sender=sender,
#                 recipient=participant,
#             )
#             db.add(new_notification)
#             await db.commit()


# 운동 약속 참가 요청 알림 생성
# 보내는 사람 : 새로운 참가자
# 받는 사람 : 운동 약속 생성자
# 알림 발생 시점 : 새로운 참가자가 운동 약속 생성자에게 요청을 보낼 때
# async def create_notification_workout_request(
#     db: AsyncSession,
#     admin_user_id: UUID,
#     new_participant_id: UUID,
#     workout_promise_id: UUID,
#     notification: NotificationWorkoutBase,
# ) -> None:
#     async with db.begin():
#         sender = await get_my_info_by_id(new_participant_id, db)
#         recipient = await get_workout_participant_by_ids(
#             db, admin_user_id, workout_promise_id
#         )

#         new_notification = NotificationWorkout(
#             **notification.dict(),
#             sender_id=new_participant_id,
#             recipient_id=recipient.id,
#             sender=sender,
#             recipient=recipient,
#         )
#         db.add(new_notification)
#         await db.commit()


# 운동 약속 참가 요청 수락 알림 생성
# 보내는 사람 : 운동 약속 생성자
# 받는 사람 : 새로운 참가자
# 알림 발생 시점 : 운동 약속 생성자가 새로운 참가자의 요청을 수락할 때
# async def create_notification_workout_request_accept(
#     db: AsyncSession,
#     admin_user_id: UUID,
#     new_participant_id: UUID,
#     workout_promise_id: UUID,
#     notification: NotificationWorkoutBase,
# ) -> None:
#     async with db.begin():
#         sender = await get_my_info_by_id(admin_user_id, db)
#         recipient = await get_workout_participant_by_ids(
#             db, new_participant_id, workout_promise_id
#         )

#         new_notification = NotificationWorkout(
#             **notification.dict(),
#             sender_id=admin_user_id,
#             recipient_id=recipient.id,
#             sender=sender,
#             recipient=recipient,
#         )
#         db.add(new_notification)
#         await db.commit()


# 운동 약속 참가 요청 거절 알림 생성
# 보내는 사람 : 운동 약속 생성자
# 받는 사람 : 새로운 참가자
# 알림 발생 시점 : 운동 약속 생성자가 새로운 참가자의 요청을 거절할 때
# async def create_notification_workout_request_reject(
#     db: AsyncSession,
#     admin_user_id: UUID,
#     new_participant_id: UUID,
#     workout_promise_id: UUID,
#     notification: NotificationWorkoutBase,
# ) -> None:
#     async with db.begin():
#         sender = await get_my_info_by_id(admin_user_id, db)
#         recipient = await get_workout_participant_by_ids(
#             db, new_participant_id, workout_promise_id
#         )

#         new_notification = NotificationWorkout(
#             **notification.dict(),
#             sender_id=admin_user_id,
#             recipient_id=recipient.id,
#             sender=sender,
#             recipient=recipient,
#         )
#         db.add(new_notification)
#         await db.commit()


# 운동 약속 모집 완료 알림 생성
# 보내는 사람 : 운동 약속 생성자
# 받는 사람 : 운동 약속 생성자 제외 운동 참가자 모두
# 알림 발생 시점 : 운동 약속 생성자가 운동 약속 모집을 완료할 때
# async def create_notification_workout_recruit_end(
#     db: AsyncSession,
#     admin_user_id: UUID,
#     workout_promise: WorkoutPromise,
#     notification: NotificationWorkoutBase,
# ) -> None:
#     async with db.begin():
#         sender = await get_my_info_by_id(admin_user_id, db)
#         participants = workout_promise.participants

#         for participant in participants:
#             # 운동 약속 생성자 제외
#             if participant.user_id == admin_user_id:
#                 continue
#             new_notification = NotificationWorkout(
#                 **notification.dict(),
#                 sender_id=admin_user_id,
#                 recipient_id=participant.id,
#                 sender=sender,
#                 recipient=participant,
#             )
#             db.add(new_notification)
#             await db.commit()
