from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select

import app.models as models
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workout_promise import GymInfo, WorkoutParticipant, WorkoutPromise
from app.schemas.workout_promise import WorkoutParticipantBase, WorkoutPromiseBase


async def get_workout_promise_by_id(
    workout_promise_id: UUID, db: AsyncSession
) -> WorkoutPromise:
    stmt = select(WorkoutPromise).where(WorkoutPromise.id == workout_promise_id)
    workout_promise = await db.execute(stmt).scalars().first()
    if not workout_promise:
        raise HTTPException(status_code=404, detail="Workout Promise is not found")
    return workout_promise


async def create_workout_promise(
    workout_promise: WorkoutPromiseBase, db: AsyncSession
) -> WorkoutPromise:
    db_gym = await get_gym_info_by_id(workout_promise.gym_info_id, db)
    new_workout_promise = WorkoutPromise(**workout_promise.dict())
    db_gym.workout_promises.append(new_workout_promise)
    db.add(db_gym)
    await db.commit()
    await db.refresh(new_workout_promise)
    return new_workout_promise


async def get_gym_info_by_id(gym_id: UUID, db: AsyncSession) -> GymInfo:
    stmt = select(GymInfo).where(GymInfo.id == gym_id)
    gym = await db.execute(stmt).scalars().first()
    if not gym:
        raise HTTPException(status_code=404, detail="Gym is not found")
    return gym


async def get_workout_participant_by_ids(
    user_id: UUID, workout_promise_id: UUID, db: AsyncSession
) -> WorkoutParticipant:
    stmt = select(WorkoutParticipant).where(
        WorkoutParticipant.user_id == user_id
        and WorkoutParticipant.workout_promise_id == workout_promise_id
    )
    workout_participant = await db.execute(stmt).scalars().first()
    if not workout_participant:
        raise HTTPException(status_code=404, detail="Workout Participant is not found")
    return workout_participant


async def create_workout_participant(
    workout_promise_id: UUID,
    workout_participant: WorkoutParticipantBase,
    db: AsyncSession,
) -> WorkoutParticipant:
    db_workout_promise = await get_workout_promise_by_id(workout_promise_id, db)

    db_w_p = await get_workout_participant_by_ids(
        workout_participant.user_id, workout_promise_id, db
    )
    if db_w_p:
        raise HTTPException(status_code=400, detail="Already joined workout promise")

    if db_workout_promise.admin_user_id == workout_participant.user_id:
        raise HTTPException(status_code=400, detail="You are the owner of this promise")

    if len(db_workout_promise.participants) >= db_workout_promise.max_participants:
        raise HTTPException(status_code=400, detail="Workout Promise is full")

    new_db_workout_participant = WorkoutParticipant(**workout_participant.dict())
    db_workout_promise.participants.append(new_db_workout_participant)
    db.add(db_workout_promise)
    await db.commit()
    await db.refresh(new_db_workout_participant)
    return new_db_workout_participant


async def delete_workout_participant(
    workout_promise_id: UUID,
    user_id: UUID,
    db: AsyncSession,
):
    stmt = select(WorkoutParticipant).where(
        WorkoutParticipant.workout_promise_id == workout_promise_id,
        WorkoutParticipant.user_id == user_id,
    )
    participant = await db.execute(stmt).scalars().first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant is not found")
    await db.delete(participant)
    await db.commit()
    return {"message": "Successfully deleted"}
