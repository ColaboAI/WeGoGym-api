from uuid import UUID
from fastapi import APIRouter, Body, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import UnauthorizedException
from app.core.fastapi.dependencies.premission import (
    IsAuthenticated,
    PermissionDependency,
)
from app.core.helpers.cache import Cache
from app.schemas.workout_promise import (
    GymInfoBase,
    WorkoutParticipantBase,
    WorkoutParticipantRead,
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
    delete_workout_promise_by_id,
    get_recruiting_workout_promise_list,
    get_workout_promise_by_id,
    get_workout_promise_list,
    get_workout_promise_list_joined_by_me,
    get_workout_promise_list_written_by_me,
    update_workout_participant_by_admin,
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
@Cache.cached(prefix="workout-promise-list", ttl=60)
async def get_workout_promises(
    session: AsyncSession = Depends(get_db_transactional_session),
    limit: int = Query(10, description="Limit"),
    offset: int = Query(0, description="offset"),
):
    total, wp_list = await get_workout_promise_list(session, limit, offset)

    return {
        "total": total,
        "items": wp_list,
        "next_cursor": offset + len(wp_list)
        if total and total > offset + len(wp_list)
        else None,
    }


# 모집 중인 운동 약속 정보 조회 엔드포인트
@workout_promise_router.get(
    "/recruiting",
    response_model=WorkoutPromiseListResponse,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
@Cache.cached(prefix="workout-promise-recruiting-list", ttl=60)
async def get_recruiting_workout_promises(
    session: AsyncSession = Depends(get_db_transactional_session),
    limit: int = Query(10, description="Limit"),
    offset: int = Query(0, description="offset"),
):
    total, wp_list = await get_recruiting_workout_promise_list(session, limit, offset)
    return {
        "total": total,
        "items": wp_list,
        "next_cursor": offset + len(wp_list)
        if total and total > offset + len(wp_list)
        else None,
    }


@workout_promise_router.get(
    "/me",
    response_model=WorkoutPromiseListResponse,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def get_workout_promises_written_by_me(
    req: Request,
    session: AsyncSession = Depends(get_db_transactional_session),
    limit: int = Query(10, description="Limit"),
    offset: int = Query(0, description="offset"),
):
    total, wp_list = await get_workout_promise_list_written_by_me(
        session,
        req.user.id,
        limit,
        offset,
    )

    return {
        "total": total,
        "items": wp_list,
        "next_cursor": offset + len(wp_list)
        if total and total > offset + len(wp_list)
        else None,
    }


@workout_promise_router.get(
    "/participant/me",
    response_model=WorkoutPromiseListResponse,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def get_workout_promises_joined_by_me(
    req: Request,
    session: AsyncSession = Depends(get_db_transactional_session),
    limit: int = Query(10, description="Limit"),
    offset: int = Query(0, description="offset"),
):
    total, wp_list = await get_workout_promise_list_joined_by_me(
        session,
        req.user.id,
        limit,
        offset,
    )

    return {
        "total": total,
        "items": wp_list,
        "next_cursor": offset + len(wp_list)
        if total and total > offset + len(wp_list)
        else None,
    }


@workout_promise_router.get(
    "/{workout_promise_id}",
    response_model=WorkoutPromiseRead,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
@Cache.cached(prefix="workout-promise-detail", ttl=60)
async def get_workout_promise(
    workout_promise_id: UUID,
    session: AsyncSession = Depends(get_db_transactional_session),
):
    wp = await get_workout_promise_by_id(session, workout_promise_id)
    return wp


# 운동 약속 정보 생성 엔드포인트
@workout_promise_router.post(
    "",
    response_model=WorkoutPromiseRead,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def make_new_workout_promise(
    request: Request,
    workout_promise: WorkoutPromiseBase = Body(...),
    gym_info: GymInfoBase = Body(None),
    db: AsyncSession = Depends(get_db_transactional_session),
):
    if request.user.id:
        db_workout_promise = await create_workout_promise(
            db, request.user.id, workout_promise, gym_info
        )
    else:
        raise UnauthorizedException("You are not authenticated user")

    await Cache.remove_by_prefix("workout-promise-detail")
    await Cache.remove_by_prefix("workout-promise-list")
    await Cache.remove_by_prefix("workout-promise-recruiting-list")
    return db_workout_promise


# 운동 약속에 참여하기
@workout_promise_router.post(
    "/{workout_promise_id}/participants",
    response_model=WorkoutParticipantRead,
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def join_workout_promise(
    req: Request,
    workout_promise_id: UUID,
    req_body: WorkoutParticipantBase = Body(...),
    db: AsyncSession = Depends(get_db_transactional_session),
):
    db_w_pp = await create_workout_participant(
        db, workout_promise_id, req_body, req.user.id
    )
    await Cache.remove_by_prefix("workout-promise-detail")

    return db_w_pp


# 운동 약속에 삭제하기
@workout_promise_router.delete(
    "/{workout_promise_id}",
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def delete_workout_promise(
    workout_promise_id: UUID,
    db: AsyncSession = Depends(get_db_transactional_session),
):
    msg = await delete_workout_promise_by_id(db, workout_promise_id)
    await Cache.remove_by_prefix("workout-promise-list")
    await Cache.remove_by_prefix("workout-promise-recruiting-list")
    return msg


# 운동 약속에 참여 취소하기
@workout_promise_router.delete("/{workout_promise_id}/participants/{user_id}")
async def leave_workout_promise(
    workout_promise_id: UUID,
    user_id: UUID,
    db: AsyncSession = Depends(get_db_transactional_session),
):
    msg = await delete_workout_participant(db, workout_promise_id, user_id)
    await Cache.remove_by_prefix("workout-promise-detail")
    await Cache.remove_by_prefix("workout-promise-list")
    await Cache.remove_by_prefix("workout-promise-recruiting-list")
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
    gym_info: GymInfoBase = Body(None),
    db: AsyncSession = Depends(get_db_transactional_session),
):
    updated_w_p = await update_workout_promise_by_id(
        db, workout_promise_id, workout_promise, gym_info
    )
    await Cache.remove_by_prefix("workout-promise-detail")
    await Cache.remove_by_prefix("workout-promise-list")
    await Cache.remove_by_prefix("workout-promise-recruiting-list")
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
    updated_w_pp = await update_workout_participant_by_admin(
        db, req.user.id, workout_promise_id, user_id, update_req
    )
    await Cache.remove_by_prefix("workout-promise-detail")
    await Cache.remove_by_prefix("workout-promise-list")
    await Cache.remove_by_prefix("workout-promise-recruiting-list")

    return updated_w_pp
