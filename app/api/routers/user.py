from fastapi import APIRouter, Body, Depends, File, Form, Query, Request, UploadFile
from pydantic import Json
from app.core.fastapi.dependencies.premission import (
    AllowAll,
    IsAdmin,
    IsAuthenticated,
    PermissionDependency,
)
from app.schemas import ExceptionResponseSchema
from app.schemas.user import (
    LoginResponse,
    MyInfoRead,
    UserListRead,
    UserCreate,
    UserUpdate,
    LoginRequest,
)
from app.services.aws_service import upload_image_to_s3
from app.session import get_db_transactional_session
from app.services.user_service import (
    UserService,
    get_my_info_by_id,
    update_my_info_by_id,
)
from sqlalchemy.ext.asyncio import AsyncSession

user_router = APIRouter()

# For testing?
@user_router.get(
    "",
    response_model=UserListRead,
    summary="Get users with limits",
    description="Get users (Only admin user can use this API)",
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([IsAdmin]))],
)
async def get_user_list(
    limit: int = Query(10, description="Limit"),
    offset: int = Query(None, description="offset(= skip)"),
):
    t, res = await UserService().get_user_list(limit=limit, offset=offset)
    return {"total": t, "users": res}


# TODO: get firebase token or user id and check if user exists
# user profile image upload to s3
@user_router.post(
    "/register",
    response_model=LoginResponse,
    responses={"400": {"model": ExceptionResponseSchema}},
    summary="Register New User",
    description="Create user with phone number and username and return tokens",
    response_model_exclude={"id"},
    dependencies=[Depends(PermissionDependency([AllowAll]))],
)
async def create_user(
    create_req: UserCreate,
):
    usr_svc = UserService()
    await usr_svc.create_user(**create_req.dict())
    token = await usr_svc.login(phone_number=create_req.phone_number)

    return {"token": token.token, "refresh_token": token.refresh_token}


# TODO: get firebase token or user id
@user_router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login",
    description="Login with phone number and return tokens",
    responses={"404": {"model": ExceptionResponseSchema}},
)
async def login(req: LoginRequest):
    token = await UserService().login(phone_number=req.phone_number)
    return {"token": token.token, "refresh_token": token.refresh_token}


@user_router.get(
    "/me",
    response_model=MyInfoRead,
    summary="Get My Info",
    description="Get my info with token",
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def get_my_info(
    req: Request,
    session: AsyncSession = Depends(get_db_transactional_session),
):
    user = await get_my_info_by_id(req.user.id, session)

    return user


@user_router.patch(
    "/me",
    response_model=MyInfoRead,
    summary="Update My Info",
    description="Update my info with token",
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def patch_my_info(
    req: Request,
    data: UserUpdate = Body(...),
    file: UploadFile | None = File(None, description="새로운 프로필 사진"),
    session: AsyncSession = Depends(get_db_transactional_session),
):
    img_url: str = upload_image_to_s3(file, req.user.id) if file else None
    if img_url:
        data.profile_pic = img_url
    else:
        del data.profile_pic
    user = await update_my_info_by_id(req.user.id, data, session)
    return user
