from datetime import datetime, timezone
from uuid import UUID
from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    Query,
    Request,
    UploadFile,
    BackgroundTasks,
)
from app.core.exceptions.base import BadRequestException
from app.core.fastapi.dependencies.premission import (
    AllowAll,
    IsAdmin,
    IsAuthenticated,
    PermissionDependency,
)
from app.core.helpers.cache import Cache
from app.schemas import ExceptionResponseSchema
from app.schemas.user import (
    LoginResponse,
    MyInfoRead,
    RecommendedUser,
    UserListRead,
    UserCreate,
    UserUpdate,
    LoginRequest,
)
from app.services.aws_service import upload_image_to_s3
from app.session import get_db_transactional_session
from app.services.user_service import (
    UserService,
    check_user_phone_number,
    check_username,
    delete_user_by_id,
    get_my_info_by_id,
    get_random_user_with_limit,
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


# check phone number or username exists


@user_router.get(
    "/check",
    status_code=204,
    summary="Check phone number or username exists",
    description="Check phone number or username exists",
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([AllowAll]))],
)
async def check_user_exists(
    db: AsyncSession = Depends(get_db_transactional_session),
    phone_number: str = Query(None, description="Phone number"),
    username: str = Query(None, description="Username"),
):
    if not phone_number and not username:
        raise BadRequestException(
            "You must provide phone number or username to check user exists"
        )

    out = {}
    if phone_number:
        out["phone_number"] = await check_user_phone_number(
            db, phone_number=phone_number
        )
    if username:
        out["username"] = await check_username(db, username=username)

    return out


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

    return token


@user_router.delete(
    "/unregister",
    summary="Unregister user",
    description="Unregister user From WeGoGym",
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def delete_user(
    req: Request,
    session: AsyncSession = Depends(get_db_transactional_session),
    bg=BackgroundTasks,
):
    await delete_user_by_id(req.user.id, session, bg)
    return {"message": f"User {req.user.id} deleted successfully"}


# TODO: get firebase token or user id
@user_router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login",
    description="Login with phone number and return tokens",
    responses={"404": {"model": ExceptionResponseSchema}},
)
async def login(req: LoginRequest):
    res = await UserService().login(phone_number=req.phone_number)
    return res


@user_router.get(
    "/logout",
    summary="Logout",
    description="Logout with token",
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def logout(req: Request):
    await UserService().logout(req.user.id)
    return {"message": "Logout Success"}


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
    img_url = upload_image_to_s3(file, req.user.id) if file else None
    if img_url:
        data.profile_pic = img_url
    else:
        del data.profile_pic
    user = await update_my_info_by_id(req.user.id, data, session)
    return user


@user_router.patch(
    "/me/fcm-token",
    status_code=204,
    summary="Update My FCM Token",
    description="Update my FCM Token with token",
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def patch_my_fcm_token(
    req: Request,
    fcm_token: str = Body(...),
    session: AsyncSession = Depends(get_db_transactional_session),
):
    data = UserUpdate(fcm_token=fcm_token, last_active_at=datetime.now(timezone.utc))
    await update_my_info_by_id(req.user.id, data, session)
    return


@user_router.get(
    "/recommended-mates",
    response_model=list[RecommendedUser],
    summary="Get Recommended Users",
    description="Get recommended users with token",
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def get_recommended_users(
    req: Request,
    session: AsyncSession = Depends(get_db_transactional_session),
    limit: int = Query(3, description="Limit"),
):
    users = await get_random_user_with_limit(session, req.user.id, limit)

    return users


@user_router.get(
    "/{user_id}",
    response_model=MyInfoRead,
    summary="Get User Info",
    description="Get user info with token",
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
@Cache.cached(ttl=60 * 60)
async def get_user_info(
    user_id: UUID,
    session: AsyncSession = Depends(get_db_transactional_session),
):
    user = await get_my_info_by_id(user_id, session)

    return user
