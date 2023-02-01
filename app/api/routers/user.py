from fastapi import APIRouter, Depends, Query
from app.core.fastapi.dependencies.premission import IsAdmin, PermissionDependency
from app.models.user import User
from app.schemas import ExceptionResponseSchema
from app.schemas.user import LoginResponse, UserRead, UserCreate, UserUpdate
from app.session import get_db_transactional_session
from app.services.user_service import UserService
from sqlalchemy.ext.asyncio import AsyncSession

user_router = APIRouter()

# For testing?
@user_router.get(
    "",
    response_model=list[UserRead],
    summary="Get users with limits",
    description="Get users",
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([IsAdmin]))],
)
async def get_user_list(
    limit: int = Query(10, description="Limit"),
    prev_id: str = Query(None, description="Previous ID"),
    session: AsyncSession = Depends(get_db_transactional_session),
):
    res = await UserService().get_user_list(limit=limit, prev_id=prev_id)
    return res


@user_router.post(
    "",
    response_model=LoginResponse,
    responses={"400": {"model": ExceptionResponseSchema}},
    summary="Register New User",
    description="Create user with phone number and username and return tokens",
    response_model_exclude={"id"},
)
async def create_user(
    create_req: UserCreate,
    session: AsyncSession = Depends(get_db_transactional_session),
):
    usr_svc = UserService(session)
    await usr_svc.create_user(**create_req.dict())
    token = await usr_svc.login(phone_number=create_req.phone_number)

    return {"token": token.token, "refresh_token": token.refresh_token}


@user_router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login",
    description="Login with phone number and return tokens",
    responses={"404": {"model": ExceptionResponseSchema}},
)
async def login(
    phone_number: str,
    session: AsyncSession = Depends(get_db_transactional_session),
):
    token = await UserService().login(phone_number=phone_number)
    return {"token": token.token, "refresh_token": token.refresh_token}
