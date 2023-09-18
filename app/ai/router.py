from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4
from fastapi.responses import UJSONResponse
import ujson
from app.ai import service as ai_service
from app.ai.schema import AiCoachingResponse
from app.core.fastapi.dependencies.premission import AllowAll, IsAuthenticated, PermissionDependency
from app.utils.user import get_user_id_from_request

router = APIRouter(
    prefix="/ai",
    tags=["ai"],
)


@router.get(
    "/coachings",
    status_code=200,
    summary="Get all ai coaching",
)
async def get_all_ai_coaching():
    return await ai_service.get_all_ai_coaching()


@router.get(
    "/coachings/{id}",
    status_code=200,
    summary="Get ai coaching where post id",
    response_model=AiCoachingResponse,
    dependencies=[
        Depends(PermissionDependency([AllowAll])),
    ],
)
async def get_ai_coaching_where_id(id: int, user_id: Annotated[UUID4, None] = Depends(get_user_id_from_request)):
    print("user_id!!!!!", user_id)
    return await ai_service.get_ai_coaching_where_post_id(id, user_id)


@router.post(
    "/coachings/{id}/like",
    status_code=201,
    response_model=AiCoachingResponse,
    dependencies=[
        Depends(PermissionDependency([IsAuthenticated])),
    ],
)
async def post_ai_coaching_like(id: int, user_id: UUID4 = Depends(get_user_id_from_request)):
    return await ai_service.create_or_update_ai_coaching_like(id, user_id, 1)


@router.post(
    "/coachings/{id}/unlike",
    status_code=201,
    response_model=AiCoachingResponse,
    dependencies=[
        Depends(PermissionDependency([IsAuthenticated])),
    ],
)
async def post_ai_coaching_unlike(id: int, user_id: UUID4 = Depends(get_user_id_from_request)):
    return await ai_service.create_or_update_ai_coaching_like(id, user_id, 0)
