from uuid import UUID
from sqlalchemy import select, func

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions.workout_promise import NotAdminOfWorkoutPromiseException

from app.models.workout_promise import GymInfo, WorkoutParticipant, WorkoutPromise
from app.schemas.workout_promise import (
    GymInfoBase,
    GymInfoUpdate,
    WorkoutParticipantBase,
    WorkoutParticipantUpdate,
    WorkoutPromiseBase,
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


async def get_gym_info_by_id(db: AsyncSession, gym_info_id: UUID) -> GymInfo:
    stmt = select(GymInfo).where(GymInfo.id == gym_info_id)
    res = await db.execute(stmt)
    gym = res.scalars().first()
    if not gym:
        raise GymInfoNotFoundException
    return gym


async def get_gym_info_by_name_and_addr(
    db: AsyncSession, gym_info_name: str, gym_info_addr: str
) -> GymInfo | None:
    stmt = select(GymInfo).where(
        GymInfo.address == gym_info_addr, GymInfo.name == gym_info_name
    )
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


async def update_gym_info_by_id(
    db: AsyncSession, gym_info_id: UUID, gym_info: GymInfoUpdate
) -> GymInfo:
    gym = await get_gym_info_by_id(db, gym_info_id)
    for k, v in gym_info.get_update_dict().items():
        setattr(gym, k, v)
    await db.commit()
    await db.refresh(gym)
    return gym


async def get_workout_promise_list(
    db: AsyncSession,
    limit: int = 10,
    offset: int | None = None,
) -> tuple[int | None, list[WorkoutPromise]]:
    stmt = (
        select(WorkoutPromise)
        .order_by(WorkoutPromise.created_at.desc())
        .options(selectinload(WorkoutPromise.chat_room))
        .options(selectinload(WorkoutPromise.participants))
        .options(selectinload(WorkoutPromise.gym_info))
        .options(selectinload(WorkoutPromise.admin_user))
        .where(WorkoutPromise.is_private.is_(False))
    )
    t_stmt = (
        select(func.count("*"))
        .where(WorkoutPromise.is_private.is_(False))
        .select_from(WorkoutPromise)
    )

    if offset:
        stmt = stmt.offset(offset)

    if limit:
        stmt = stmt.limit(limit)

    total = await db.execute(t_stmt)
    result = await db.execute(stmt)

    return total.scalars().first(), result.scalars().all()


async def get_workout_promise_with_participants(
    db: AsyncSession, workout_promise_id: UUID
) -> WorkoutPromise:
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


async def get_workout_promise_by_id(
    db: AsyncSession, workout_promise_id: UUID
) -> WorkoutPromise:
    stmt = select(WorkoutPromise).where(WorkoutPromise.id == workout_promise_id)
    res = await db.execute(stmt)
    workout_promise = res.scalars().first()
    if not workout_promise:
        raise WorkoutPromiseNotFoundException
    return workout_promise


async def create_workout_promise(
    db: AsyncSession,
    admin_user_id: UUID,
    workout_promise: WorkoutPromiseBase,
    gym_info: GymInfoBase | None = None,
) -> WorkoutPromise:
    new_workout_promise = WorkoutPromise(
        **workout_promise.dict(
            exclude_unset=True,
        )
    )
    new_workout_promise.admin_user_id = admin_user_id

    db_gym_info = None
    if gym_info:
        db_gym_info = await get_gym_info_or_create(db, gym_info)
        new_workout_promise.gym_info = db_gym_info

    # Make Admin Participant
    admin_participant = WorkoutParticipant(
        user_id=admin_user_id,
        is_admin=True,
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
async def update_workout_promise_by_id(
    db: AsyncSession,
    workout_promise_id: UUID,
    workout_promise: WorkoutPromiseUpdate,
    gym_info: GymInfoBase | None = None,
) -> WorkoutPromise:
    db_workout_promise = await get_workout_promise_by_id(db, workout_promise_id)
    if gym_info:
        db_gym_info = await get_gym_info_or_create(db, gym_info)
        db_workout_promise.gym_info = db_gym_info

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
    stmt = select(WorkoutParticipant).where(
        WorkoutParticipant.user_id == user_id,
        WorkoutParticipant.workout_promise_id == workout_promise_id,
    )
    res = await db.execute(stmt)
    workout_participant = res.scalars().first()
    if not workout_participant:
        raise WorkoutParticipantNotFoundException
    return workout_participant


async def create_workout_participant(
    db: AsyncSession,
    workout_promise_id: UUID,
    workout_participant: WorkoutParticipantBase,
) -> WorkoutParticipant:
    db_workout_promise = await get_workout_promise_by_id(db, workout_promise_id)
    db_w_pp = await get_workout_participant_by_ids(
        db, workout_participant.user_id, workout_promise_id
    )
    if db_w_pp:
        raise AlreadyJoinedWorkoutPromiseException
    # TODO: Fix this logic
    max_p = db_workout_promise.max_participants
    if max_p is not None and max_p > 0:
        if len(db_workout_promise.participants) >= max_p:
            raise WorkoutPromiseIsFullException
    else:
        raise WorkoutPromiseIsWrongException

    new_db_workout_participant = WorkoutParticipant(**workout_participant.dict())
    db_workout_promise.participants.append(new_db_workout_participant)
    db.add(db_workout_promise)
    await db.commit()
    await db.refresh(new_db_workout_participant)
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


async def update_workout_participant_(
    db: AsyncSession,
    req_user_id: UUID,
    workout_promise_id: UUID,
    user_id: UUID,
    workout_participant: WorkoutParticipantUpdate,
) -> WorkoutParticipant:
    db_workout_participant = await get_workout_participant_by_ids(
        db, user_id, workout_promise_id
    )
    for k, v in workout_participant.get_update_dict().items():
        setattr(db_workout_participant, k, v)
    if workout_participant.is_admin:
        stmt = select(WorkoutPromise.admin_user_id).where(
            WorkoutPromise.id == workout_promise_id
        )
        res = await db.execute(stmt)
        admin_user_id = res.scalars().first()
        if admin_user_id != req_user_id:
            raise NotAdminOfWorkoutPromiseException(
                "Failed to update is_admin in WorkoutParticipant"
            )
        else:
            db_workout_participant.is_admin = workout_participant.is_admin

    await db.commit()
    await db.refresh(db_workout_participant)
    return db_workout_participant
