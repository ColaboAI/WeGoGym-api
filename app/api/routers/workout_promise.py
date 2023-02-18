from uuid import UUID
from fastapi import APIRouter, Body, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.fastapi.dependencies.premission import (
    IsAuthenticated,
    PermissionDependency,
)
from app.schemas.workout_promise import (
    GymInfoBase,
    WorkoutParticipantBase,
    WorkoutParticipantUpdate,
    WorkoutPromiseBase,
    WorkoutPromiseListResponse,
    WorkoutPromiseRead,
    WorkoutPromiseUpdate,
)
from app.services.workout_promise_service import (
    create_workout_participant,
    create_workout_promise,
    delete_workout_participant,
    get_workout_promise_list,
    update_workout_participant_,
    update_workout_promise_by_id,
)
from app.session import get_db_transactional_session

workout_promise_router = APIRouter()

# 운동 약속 정보 조회 엔드포인트
@workout_promise_router.get(
    "",
    response_model=WorkoutPromiseListResponse,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def get_workout_promise(
    session: AsyncSession = Depends(get_db_transactional_session),
    limit: int = 10,
    offset: int = 0,
):
    wp = await get_workout_promise_list(session, limit, offset)
    return wp


# 운동 약속 정보 생성 엔드포인트
@workout_promise_router.post(
    "",
    response_model=WorkoutPromiseRead,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def make_new_workout_promise(
    workout_promise: WorkoutPromiseBase = Body(...),
    gym_info: GymInfoBase = Body(...),
    db: AsyncSession = Depends(get_db_transactional_session),
):
    db_workout_promise = create_workout_promise(db, workout_promise, gym_info)
    return db_workout_promise


# 운동 약속에 참여하기
@workout_promise_router.post(
    "/{workout_promise_id}/participants",
    response_model=WorkoutParticipantBase,
)
async def join_workout_promise(
    workout_promise_id: UUID,
    req_body: WorkoutParticipantBase = Body(...),
    db: AsyncSession = Depends(get_db_transactional_session),
):
    db_w_pp = await create_workout_participant(db, workout_promise_id, req_body)
    return db_w_pp


# 운동 약속에 참여 취소하기
@workout_promise_router.delete("/{workout_promise_id}/participants/{user_id}")
async def leave_workout_promise(
    workout_promise_id: UUID,
    user_id: UUID,
    db: AsyncSession = Depends(get_db_transactional_session),
):

    msg = await delete_workout_participant(db, workout_promise_id, user_id)

    return msg


# 운동 약속 정보 수정 엔드포인트
@workout_promise_router.patch(
    "/{workout_promise_id}",
    response_model=WorkoutPromiseRead,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def update_workout_promise(
    workout_promise_id: UUID,
    workout_promise: WorkoutPromiseUpdate = Body(...),
    gym_info: GymInfoBase = Body(...),
    db: AsyncSession = Depends(get_db_transactional_session),
):

    updated_w_p = await update_workout_promise_by_id(
        db, workout_promise_id, workout_promise, gym_info
    )
    return updated_w_p


# 방장이 참여자 상태 관리 (참여자 승인, 참여자 거절, 참여자 강퇴)
@workout_promise_router.patch(
    "/{workout_promise_id}/participants/{user_id}",
    response_model=WorkoutParticipantBase,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def update_workout_participant(
    req: Request,
    workout_promise_id: UUID,
    user_id: UUID,
    update_req: WorkoutParticipantUpdate = Body(...),
    db: AsyncSession = Depends(get_db_transactional_session),
):

    updated_w_pp = update_workout_participant_(
        db, req.user.id, workout_promise_id, user_id, update_req
    )
    return updated_w_pp
