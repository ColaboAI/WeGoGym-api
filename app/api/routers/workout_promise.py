from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.fastapi.dependencies.premission import (
    IsAuthenticated,
    PermissionDependency,
)
from app.models import WorkoutPromise
from app.models.workout_promise import WorkoutParticipant
from app.schemas.workout_promise import (
    WorkoutParticipantBase,
    WorkoutPromiseCreate,
    WorkoutPromiseRead,
    WorkoutPromiseUpdate,
)
from app.session import get_db_transactional_session
from sqlalchemy import select

workout_promise_router = APIRouter()

# 운동 약속 정보 조회 엔드포인트
@workout_promise_router.get(
    "",
    response_model=list[WorkoutPromiseRead],
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def get_workout_promise(session: Session = Depends(get_db_transactional_session)):
    exercises = session.execute(select(WorkoutPromise)).scalars().all()
    return exercises


# 운동 약속 정보 생성 엔드포인트
@workout_promise_router.post(
    "",
    response_model=WorkoutPromiseRead,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def create_workout_promise(
    workout_promise: WorkoutPromiseCreate,
    db: Session = Depends(get_db_transactional_session),
):
    db_exercise = WorkoutPromise(**workout_promise.dict())
    db.add(db_exercise)
    await db.commit()
    await db.refresh(db_exercise)
    return db_exercise


# 운동 약속에 참여하기
@workout_promise_router.post("/{workout_promise_id}/participants")
async def join_workout_promise(
    workout_promise_id: int,
    user_id: int,
    db: Session = Depends(get_db_transactional_session),
):

    stmt = select(WorkoutPromise).where(WorkoutPromise.id == workout_promise_id)
    exercise = db.execute(stmt).scalars().first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Workout Promise is not found")
    if len(exercise.participants) >= exercise.max_participants:
        raise HTTPException(status_code=400, detail="Workout Promise is full")

    stmt = select(WorkoutParticipant).where(
        WorkoutParticipant.exercise_id == workout_promise_id,
        WorkoutParticipant.user_id == user_id,
    )
    participant = db.execute(stmt).scalars().first()

    if participant:
        raise HTTPException(status_code=400, detail="Already joined participant")
    new_participant = WorkoutParticipant(
        user_id=user_id, workout_promise_id=workout_promise_id
    )
    db.add(new_participant)
    await db.commit()
    await db.refresh(new_participant)
    return new_participant


# 운동 약속에 참여 취소하기
@workout_promise_router.delete("/{workout_promise_id}/participants")
async def leave_workout_promise(
    workout_promise_id: int,
    user_id: int,
    db: Session = Depends(get_db_transactional_session),
):
    stmt = select(WorkoutParticipant).where(
        WorkoutParticipant.exercise_id == workout_promise_id,
        WorkoutParticipant.user_id == user_id,
    )
    participant = db.execute(stmt).scalars().first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant is not found")
    await db.delete(participant)
    await db.commit()
    return {"message": "Successfully deleted"}


# 운동 약속 정보 수정 엔드포인트
@workout_promise_router.patch(
    "/{workout_promise_id}",
    response_model=WorkoutPromiseRead,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def update_workout_promise(
    workout_promise_id: int,
    workout_promise: WorkoutPromiseUpdate,
    db: Session = Depends(get_db_transactional_session),
):
    stmt = select(WorkoutPromise).where(WorkoutPromise.id == workout_promise_id)
    exercise = db.execute(stmt).scalars().first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Workout Promise is not found")
    exercise.title = workout_promise.title
    exercise.description = workout_promise.description
    exercise.max_participants = workout_promise.max_participants
    await db.commit()
    await db.refresh(exercise)
    return exercise


# 방장이 참여자 상태 관리 (참여자 승인, 참여자 거절, 참여자 강퇴)
@workout_promise_router.patch(
    "/{workout_promise_id}/participants/{user_id}",
    response_model=WorkoutParticipantBase,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def update_workout_promise_participant(
    workout_promise_id: int,
    user_id: int,
    status: WorkoutParticipantBase,
    db: Session = Depends(get_db_transactional_session),
):

    stmt = select(WorkoutParticipant).where(
        WorkoutParticipant.exercise_id == workout_promise_id,
        WorkoutParticipant.user_id == user_id,
    )
    participant = db.execute(stmt).scalars().first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant is not found")
    if status == "accept":
        participant.status = "accept"
    elif status == "reject":
        participant.status = "reject"
    elif status == "kick":
        participant.status = "kick"
    else:
        raise HTTPException(status_code=400, detail="Invalid status")
    await db.commit()
    await db.refresh(participant)
    return participant
