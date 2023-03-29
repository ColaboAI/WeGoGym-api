from uuid import UUID
from sqlalchemy import select, func

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import NotificationWorkout
from app.models.workout_promise import WorkoutParticipant, WorkoutPromise
from app.schemas.notification import (
    NotificationWorkoutBase,
)

from sqlalchemy.orm import selectinload
from app.services.user_service import get_my_info_by_id
from app.services.workout_promise_service import get_workout_participant_by_ids


# 내 운동 알림 정보 조회
async def get_notification_workout_list(
    db: AsyncSession,
    user_id: UUID,
    limit: int = 10,
    offset: int | None = 0,
) -> tuple[int | None, list[NotificationWorkout]]:
    stmt = (
        select(NotificationWorkout)
        .order_by(NotificationWorkout.created_at.desc())
        .options(
            selectinload(NotificationWorkout.sender),
            selectinload(NotificationWorkout.recipient).options(
                selectinload(WorkoutParticipant.user)
            ),
        )
        .join(NotificationWorkout.recipient)
        .where(WorkoutParticipant.user_id == user_id)
    )
    t_stmt = (
        select(func.count("*"))
        .join(NotificationWorkout.recipient)
        .where(WorkoutParticipant.user_id == user_id)
        .select_from(NotificationWorkout)
    )

    total = await db.execute(t_stmt)
    result = await db.execute(stmt)

    return total.scalar(), result.scalars().all()


# 새로운 운동 약속 참가자 알림 생성
# 보내는 사람 : 운동 약속 생성자
# 받는 사람 : 운동 약속 생성자와 새로운 참가자 제외 -> 기존의 참가자들
# 알림 발생 시점 : 운동 약속 생성자가 새로운 참가자의 요청을 수락할 때
async def create_notification_workout_new_participant(
    db: AsyncSession,
    # 운동 약속 생성자
    admin_user_id: UUID,
    # 새로운 참가자
    new_participant_user_id: UUID,
    workout_promise: WorkoutPromise,
    notification: NotificationWorkoutBase,
) -> None:
    async with db.begin():
        sender = await get_my_info_by_id(admin_user_id, db)
        participants = workout_promise.participants

        for participant in participants:
            # 운동 약속 생성자와 새로운 참가자 제외
            if (
                participant.user_id == admin_user_id
                or participant.user_id == new_participant_user_id
            ):
                continue
            new_notification = NotificationWorkout(
                **notification.dict(),
                sender_id=admin_user_id,
                recipient_id=participant.id,
                sender=sender,
                recipient=participant,
            )
            db.add(new_notification)
            await db.commit()


# 운동 약속 참가 요청 알림 생성
# 보내는 사람 : 새로운 참가자
# 받는 사람 : 운동 약속 생성자
# 알림 발생 시점 : 새로운 참가자가 운동 약속 생성자에게 요청을 보낼 때
async def create_notification_workout_request(
    db: AsyncSession,
    admin_user_id: UUID,
    new_participant_id: UUID,
    workout_promise_id: UUID,
    notification: NotificationWorkoutBase,
) -> None:
    async with db.begin():
        sender = await get_my_info_by_id(new_participant_id, db)
        recipient = await get_workout_participant_by_ids(
            db, admin_user_id, workout_promise_id
        )

        new_notification = NotificationWorkout(
            **notification.dict(),
            sender_id=new_participant_id,
            recipient_id=recipient.id,
            sender=sender,
            recipient=recipient,
        )
        db.add(new_notification)
        # await db.commit()


# 운동 약속 참가 요청 수락 알림 생성
# 보내는 사람 : 운동 약속 생성자
# 받는 사람 : 새로운 참가자
# 알림 발생 시점 : 운동 약속 생성자가 새로운 참가자의 요청을 수락할 때
async def create_notification_workout_request_accept(
    db: AsyncSession,
    admin_user_id: UUID,
    new_participant_id: UUID,
    workout_promise_id: UUID,
    notification: NotificationWorkoutBase,
) -> None:
    async with db.begin():
        sender = await get_my_info_by_id(admin_user_id, db)
        recipient = await get_workout_participant_by_ids(
            db, new_participant_id, workout_promise_id
        )

        new_notification = NotificationWorkout(
            **notification.dict(),
            sender_id=admin_user_id,
            recipient_id=recipient.id,
            sender=sender,
            recipient=recipient,
        )
        db.add(new_notification)
        await db.commit()


# 운동 약속 참가 요청 거절 알림 생성
# 보내는 사람 : 운동 약속 생성자
# 받는 사람 : 새로운 참가자
# 알림 발생 시점 : 운동 약속 생성자가 새로운 참가자의 요청을 거절할 때
async def create_notification_workout_request_reject(
    db: AsyncSession,
    admin_user_id: UUID,
    new_participant_id: UUID,
    workout_promise_id: UUID,
    notification: NotificationWorkoutBase,
) -> None:
    async with db.begin():
        sender = await get_my_info_by_id(admin_user_id, db)
        recipient = await get_workout_participant_by_ids(
            db, new_participant_id, workout_promise_id
        )

        new_notification = NotificationWorkout(
            **notification.dict(),
            sender_id=admin_user_id,
            recipient_id=recipient.id,
            sender=sender,
            recipient=recipient,
        )
        db.add(new_notification)
        await db.commit()


# 운동 약속 모집 완료 알림 생성
# 보내는 사람 : 운동 약속 생성자
# 받는 사람 : 운동 약속 생성자 제외 운동 참가자 모두
# 알림 발생 시점 : 운동 약속 생성자가 운동 약속 모집을 완료할 때
async def create_notification_workout_recruit_end(
    db: AsyncSession,
    admin_user_id: UUID,
    workout_promise: WorkoutPromise,
    notification: NotificationWorkoutBase,
) -> None:
    async with db.begin():
        sender = await get_my_info_by_id(admin_user_id, db)
        participants = workout_promise.participants

        for participant in participants:
            # 운동 약속 생성자 제외
            if participant.user_id == admin_user_id:
                continue
            new_notification = NotificationWorkout(
                **notification.dict(),
                sender_id=admin_user_id,
                recipient_id=participant.id,
                sender=sender,
                recipient=participant,
            )
            db.add(new_notification)
            await db.commit()
