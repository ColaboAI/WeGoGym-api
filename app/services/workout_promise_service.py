from uuid import UUID
from sqlalchemy import select, func

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions.workout_promise import NotAdminOfWorkoutPromiseException
from app.models.notification import NotificationWorkout
from app.models.user import User
from app.models.workout_promise import (
    GymInfo,
    PromiseLocation,
    WorkoutParticipant,
    WorkoutPromise,
)
from app.schemas.notification import NotificationWorkoutType
from app.schemas.workout_promise import (
    GymInfoBase,
    GymInfoUpdate,
    ParticipantStatus,
    PromiseLocationBase,
    WorkoutParticipantBase,
    WorkoutParticipantUpdate,
    WorkoutPromiseBase,
    WorkoutPromiseStatus,
    WorkoutPromiseUpdate,
)
from app.core.exceptions import (
    GymInfoNotFoundException,
    WorkoutPromiseNotFoundException,
    WorkoutParticipantNotFoundException,
    WorkoutPromiseIsFullException,
    WorkoutPromiseIsWrongException,
    AlreadyJoinedWorkoutPromiseException,
)

from sqlalchemy.orm import selectinload
from app.services.fcm_service import send_notification_workout
from app.services.user_service import get_my_info_by_id


async def get_gym_info_by_id(db: AsyncSession, gym_info_id: UUID) -> GymInfo:
    stmt = select(GymInfo).where(GymInfo.id == gym_info_id)
    res = await db.execute(stmt)
    gym = res.scalars().first()
    if not gym:
        raise GymInfoNotFoundException
    return gym


async def get_gym_info_by_name_and_addr(db: AsyncSession, gym_info_name: str, gym_info_addr: str) -> GymInfo | None:
    stmt = select(GymInfo).where(GymInfo.address == gym_info_addr, GymInfo.name == gym_info_name)
    res = await db.execute(stmt)
    gym: GymInfo | None = res.scalars().first()
    return gym


async def create_gym_info(db: AsyncSession, gym_info: GymInfoBase) -> GymInfo:
    new_gym_info = GymInfo(**gym_info.dict())
    db.add(new_gym_info)
    await db.commit()
    return new_gym_info


async def get_gym_info_or_create(db: AsyncSession, gym_info: GymInfoBase) -> GymInfo:
    gym = await get_gym_info_by_name_and_addr(db, gym_info.name, gym_info.address)
    if gym:
        return gym
    else:
        return await create_gym_info(db, gym_info)


async def delete_gym_info_by_id(db: AsyncSession, gym_info_id: UUID):
    gym = await get_gym_info_by_id(db, gym_info_id)
    await db.delete(gym)
    await db.commit()
    return {"message": "Successfully deleted"}


async def update_gym_info_by_id(db: AsyncSession, gym_info_id: UUID, gym_info: GymInfoUpdate) -> GymInfo:
    gym = await get_gym_info_by_id(db, gym_info_id)
    for k, v in gym_info.get_update_dict().items():
        setattr(gym, k, v)
    await db.commit()
    await db.refresh(gym)
    return gym


async def get_promise_location_by_place_name_and_addr(
    db: AsyncSession, promise_location_place_name: str, promise_location_address: str
) -> PromiseLocation | None:
    stmt = select(PromiseLocation).where(
        PromiseLocation.place_name == promise_location_place_name,
        PromiseLocation.address == promise_location_address,
    )
    res = await db.execute(stmt)
    promise_location: PromiseLocation | None = res.scalars().first()
    return promise_location


async def create_promise_location(db: AsyncSession, promise_location: PromiseLocationBase) -> PromiseLocation:
    new_promise_location = PromiseLocation(**promise_location.dict())
    db.add(new_promise_location)
    await db.commit()
    return new_promise_location


async def get_promise_location_or_create(db: AsyncSession, promise_location: PromiseLocationBase) -> PromiseLocation:
    _promise_location = await get_promise_location_by_place_name_and_addr(
        db, promise_location.place_name, promise_location.address
    )
    if _promise_location:
        return _promise_location
    else:
        return await create_promise_location(db, promise_location)


async def get_workout_promise_list(
    db: AsyncSession,
    limit: int = 10,
    offset: int | None = None,
):
    stmt = (
        select(WorkoutPromise)
        .order_by(WorkoutPromise.created_at.desc())
        .options(
            selectinload(WorkoutPromise.chat_room),
            selectinload(WorkoutPromise.participants).options(
                selectinload(WorkoutParticipant.user).load_only(
                    User.id,
                    User.username,
                    User.profile_pic,
                )
            ),
            selectinload(WorkoutPromise.promise_location),
            selectinload(WorkoutPromise.admin_user).load_only(
                User.id,
                User.username,
                User.profile_pic,
            ),
        )
        .where(WorkoutPromise.is_private.is_(False))
    )
    t_stmt = select(func.count("*")).where(WorkoutPromise.is_private.is_(False)).select_from(WorkoutPromise)

    if offset:
        stmt = stmt.offset(offset)

    if limit:
        stmt = stmt.limit(limit)

    total = await db.execute(t_stmt)
    result = await db.execute(stmt)

    return total.scalars().first(), result.scalars().all()


async def get_recruiting_workout_promise_list(
    db: AsyncSession,
    limit: int = 10,
    offset: int | None = None,
):
    stmt = (
        select(WorkoutPromise)
        .order_by(WorkoutPromise.created_at.desc())
        .options(
            selectinload(WorkoutPromise.chat_room),
            selectinload(WorkoutPromise.participants).options(
                selectinload(WorkoutParticipant.user).load_only(
                    User.id,
                    User.username,
                    User.profile_pic,
                )
            ),
            selectinload(WorkoutPromise.promise_location),
            selectinload(WorkoutPromise.admin_user).load_only(
                User.id,
                User.username,
                User.profile_pic,
            ),
        )
        .where(WorkoutPromise.is_private.is_(False))
        .where(WorkoutPromise.status == WorkoutPromiseStatus.RECRUITING)
    )
    t_stmt = (
        select(func.count("*"))
        .where(WorkoutPromise.is_private.is_(False))
        .where(WorkoutPromise.status == WorkoutPromiseStatus.RECRUITING)
        .select_from(WorkoutPromise)
    )

    if offset:
        stmt = stmt.offset(offset)

    if limit:
        stmt = stmt.limit(limit)

    total = await db.execute(t_stmt)
    result = await db.execute(stmt)

    return total.scalars().first(), result.scalars().all()


async def get_workout_promise_list_written_by_me(
    db: AsyncSession,
    user_id: UUID,
    limit: int = 10,
    offset: int | None = None,
):
    stmt = (
        select(WorkoutPromise)
        .order_by(WorkoutPromise.created_at.desc())
        .options(
            selectinload(WorkoutPromise.chat_room),
            selectinload(WorkoutPromise.participants).options(
                selectinload(WorkoutParticipant.user).load_only(
                    User.id,
                    User.username,
                    User.profile_pic,
                )
            ),
            selectinload(WorkoutPromise.promise_location),
            selectinload(WorkoutPromise.admin_user).load_only(
                User.id,
                User.username,
                User.profile_pic,
            ),
        )
        .where(WorkoutPromise.is_private.is_(False))
        .where(WorkoutPromise.admin_user_id == user_id)
    )
    t_stmt = (
        select(func.count("*"))
        .where(WorkoutPromise.is_private.is_(False))
        .where(WorkoutPromise.admin_user_id == user_id)
        .select_from(WorkoutPromise)
    )

    if offset:
        stmt = stmt.offset(offset)

    if limit:
        stmt = stmt.limit(limit)

    total = await db.execute(t_stmt)
    result = await db.execute(stmt)

    return total.scalars().first(), result.scalars().all()


async def get_workout_promise_list_joined_by_me(
    db: AsyncSession,
    user_id: UUID,
    limit: int = 10,
    offset: int | None = None,
):
    stmt = (
        select(WorkoutPromise)
        .order_by(WorkoutPromise.created_at.desc())
        .options(selectinload(WorkoutPromise.chat_room))
        .options(
            selectinload(WorkoutPromise.participants).options(selectinload(WorkoutParticipant.user)),
        )
        .options(selectinload(WorkoutPromise.promise_location))
        .options(selectinload(WorkoutPromise.admin_user))
        .where(WorkoutPromise.is_private.is_(False))
        .where(
            WorkoutPromise.participants.any(WorkoutParticipant.user_id == user_id)
            .where(WorkoutParticipant.status == ParticipantStatus.ACCEPTED)
            .where(WorkoutParticipant.is_admin.is_(False)),
        )
    )
    t_stmt = (
        select(func.count("*"))
        .where(WorkoutPromise.is_private.is_(False))
        .where(
            WorkoutPromise.participants.any(WorkoutParticipant.user_id == user_id)
            .where(WorkoutParticipant.status == ParticipantStatus.ACCEPTED)
            .where(WorkoutParticipant.is_admin.is_(False)),
        )
        .select_from(WorkoutPromise)
    )

    if offset:
        stmt = stmt.offset(offset)

    if limit:
        stmt = stmt.limit(limit)

    total = await db.execute(t_stmt)
    result = await db.execute(stmt)

    return total.scalars().first(), result.scalars().all()


async def get_workout_promise_with_participants(db: AsyncSession, workout_promise_id: UUID) -> WorkoutPromise:
    stmt = (
        select(WorkoutPromise)
        .options(
            selectinload(WorkoutPromise.participants),
        )
        .where(WorkoutPromise.id == workout_promise_id)
    )
    res = await db.execute(stmt)
    workout_promise = res.scalars().first()
    if not workout_promise:
        raise WorkoutPromiseNotFoundException
    return workout_promise


async def get_workout_promise_by_id(db: AsyncSession, workout_promise_id: UUID) -> WorkoutPromise:
    stmt = (
        select(WorkoutPromise)
        .options(
            selectinload(WorkoutPromise.participants).options(selectinload(WorkoutParticipant.user)),
            selectinload(WorkoutPromise.chat_room),
            selectinload(WorkoutPromise.promise_location),
            selectinload(WorkoutPromise.admin_user),
        )
        .where(WorkoutPromise.id == workout_promise_id)
    )
    res = await db.execute(stmt)
    workout_promise = res.scalars().first()
    if not workout_promise:
        raise WorkoutPromiseNotFoundException
    return workout_promise


async def create_workout_promise(
    db: AsyncSession,
    admin_user_id: UUID,
    workout_promise: WorkoutPromiseBase,
    promise_location: PromiseLocationBase | None = None,
) -> WorkoutPromise:
    new_workout_promise = WorkoutPromise(
        **workout_promise.dict(
            exclude_unset=True,
        )
    )
    new_workout_promise.admin_user_id = admin_user_id

    db_promise_location = None
    if promise_location:
        db_promise_location = await get_promise_location_or_create(db, promise_location)
        new_workout_promise.promise_location = db_promise_location

    # Make Admin Participant
    # FIXME: mypy error
    admin_participant = WorkoutParticipant(  # type: ignore
        user=await get_my_info_by_id(admin_user_id, db),
        user_id=admin_user_id,
        is_admin=True,
        status=ParticipantStatus.ACCEPTED,
    )

    new_workout_promise.participants.append(admin_participant)

    db.add(new_workout_promise)
    await db.commit()
    return new_workout_promise


async def delete_workout_promise_by_id(db: AsyncSession, workout_promise_id: UUID):
    workout_promise = await get_workout_promise_by_id(db, workout_promise_id)
    await db.delete(workout_promise)
    await db.commit()
    return {"message": "Workout Promise is Successfully deleted"}


# GymInfo가 endpoint 단에서 만들어졌다고 가정.
# TODO: 모집 완료 알람/푸시
async def update_workout_promise_by_id(
    db: AsyncSession,
    workout_promise_id: UUID,
    workout_promise: WorkoutPromiseUpdate,
    promise_location: PromiseLocationBase | None = None,
) -> WorkoutPromise:
    db_workout_promise = await get_workout_promise_by_id(db, workout_promise_id)
    if promise_location:
        db_promise_location = await get_promise_location_or_create(db, promise_location)
        db_workout_promise.promise_location = db_promise_location

    for k, v in workout_promise.get_update_dict().items():
        setattr(db_workout_promise, k, v)
    await db.commit()
    await db.refresh(db_workout_promise)

    return db_workout_promise


async def get_workout_participant_by_ids(
    db: AsyncSession,
    user_id: UUID,
    workout_promise_id: UUID,
) -> WorkoutParticipant:
    stmt = (
        select(WorkoutParticipant)
        .where(
            WorkoutParticipant.user_id == user_id,
            WorkoutParticipant.workout_promise_id == workout_promise_id,
        )
        .options(
            selectinload(WorkoutParticipant.workout_promise).load_only(
                WorkoutPromise.id,
                WorkoutPromise.title,
                WorkoutPromise.status,
            )
        )
    )
    res = await db.execute(stmt)
    workout_participant = res.scalars().first()
    if not workout_participant:
        raise WorkoutParticipantNotFoundException
    return workout_participant


async def get_workout_participant_id_list_by_user_id(db: AsyncSession, user_id: UUID):
    stmt = select(WorkoutParticipant.id).where(WorkoutParticipant.user_id == user_id)
    res = await db.execute(stmt)
    workout_participant_id_list = res.scalars().all()
    return workout_participant_id_list


async def create_workout_participant(
    db: AsyncSession,
    workout_promise_id: UUID,
    workout_participant: WorkoutParticipantBase,
    user_id: UUID,
) -> WorkoutParticipant:
    db_workout_promise = await get_workout_promise_by_id(db, workout_promise_id)
    db_w_pp = None
    try:
        db_w_pp = await get_workout_participant_by_ids(db, user_id, workout_promise_id)
    except WorkoutParticipantNotFoundException:
        pass

    if db_w_pp:
        raise AlreadyJoinedWorkoutPromiseException

    # TODO: Fix this logic
    max_p = db_workout_promise.max_participants
    if max_p is not None and max_p > 0:
        if len(db_workout_promise.participants) >= max_p:
            raise WorkoutPromiseIsFullException
    else:
        raise WorkoutPromiseIsWrongException
    # FIXME: mypy error
    new_db_workout_participant = WorkoutParticipant(  # type: ignore
        **workout_participant.dict(),
        user_id=user_id,
        user=await get_my_info_by_id(user_id, db),
    )
    db_workout_promise.participants.append(new_db_workout_participant)
    db.add(db_workout_promise)

    # FIXME: mypy error
    admin_participant = await get_workout_participant_by_ids(db, db_workout_promise.admin_user.id, workout_promise_id)  # type: ignore

    new_notification_workout = NotificationWorkout(  # type: ignore
        message=f"{new_db_workout_participant.status_message}",
        notification_type=NotificationWorkoutType.WORKOUT_REQUEST,
        sender_id=new_db_workout_participant.id,
        sender=new_db_workout_participant,
        recipient_id=admin_participant.id,
        recipient=admin_participant,
    )
    # send notification to admin with fcm service
    db.add(new_notification_workout)
    await db.commit()

    # SEND FCM NOTIFICATION
    await send_notification_workout(db, new_notification_workout)

    return new_db_workout_participant


async def delete_workout_participant(
    db: AsyncSession,
    workout_promise_id: UUID,
    user_id: UUID,
):
    stmt = select(WorkoutParticipant).where(
        WorkoutParticipant.workout_promise_id == workout_promise_id,
        WorkoutParticipant.user_id == user_id,
    )
    res = await db.execute(stmt)
    participant = res.scalars().first()
    if not participant:
        raise WorkoutParticipantNotFoundException
    await db.delete(participant)
    await db.commit()
    return {"message": "Successfully deleted"}


async def update_workout_participant_by_admin(
    db: AsyncSession,
    req_user_id: UUID,
    workout_promise_id: UUID,
    user_id: UUID,
    workout_participant: WorkoutParticipantUpdate,
) -> WorkoutParticipant:
    db_workout_participant = await get_workout_participant_by_ids(db, user_id, workout_promise_id)
    for k, v in workout_participant.get_update_dict().items():
        setattr(db_workout_participant, k, v)
    if workout_participant.is_admin:
        stmt = select(WorkoutPromise.admin_user_id).where(WorkoutPromise.id == workout_promise_id)
        res = await db.execute(stmt)
        admin_user_id = res.scalars().first()
        if admin_user_id != req_user_id:
            raise NotAdminOfWorkoutPromiseException("Failed to update is_admin in WorkoutParticipant")
        else:
            db_workout_participant.is_admin = workout_participant.is_admin

    db_admin_workout_participant = await get_workout_participant_by_ids(db, req_user_id, workout_promise_id)

    if workout_participant.status == ParticipantStatus.ACCEPTED:
        # FIXME: mypy error
        new_notification_workout = NotificationWorkout(  # type: ignore
            notification_type=NotificationWorkoutType.WORKOUT_ACCEPT,
            sender_id=db_admin_workout_participant.id,
            sender=db_admin_workout_participant,
            recipient_id=db_workout_participant.id,
            recipient=db_workout_participant,
        )

    elif workout_participant.status == ParticipantStatus.REJECTED:
        # FIXME: mypy error
        new_notification_workout = NotificationWorkout(  # type: ignore
            notification_type=NotificationWorkoutType.WORKOUT_REJECT,
            sender_id=db_admin_workout_participant.id,
            sender=db_admin_workout_participant,
            recipient_id=db_workout_participant.id,
            recipient=db_workout_participant,
        )

    db.add(new_notification_workout)

    await db.commit()
    await db.refresh(db_workout_participant)

    # SEND FCM NOTIFICATION
    await send_notification_workout(db, new_notification_workout)

    return db_workout_participant
