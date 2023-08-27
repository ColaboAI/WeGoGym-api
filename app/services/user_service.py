from typing import Mapping, Sequence
from fastapi import BackgroundTasks, HTTPException
from pydantic import UUID4

from sqlalchemy import delete, func, insert, or_, select, and_
from app.core.exceptions.user import UserAlreadyExistsException, UserBlockedException

from app.models import User
from app.models.user import user_block_list
from app.models.workout_promise import GymInfo
from app.schemas import LoginResponse
from app.core.exceptions import (
    DuplicatePhoneNumberOrUsernameException,
    UserNotFoundException,
)
from app.schemas.user import UserUpdate
from app.utils.token_helper import TokenHelper
from app.session import Transactional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, raiseload
from app.utils.ecs_log import logger


# User service: user adaptor for sqlalchemy
class UserService:
    @Transactional()
    async def get_user_list(
        self,
        session: AsyncSession,
        limit: int = 10,
        offset: int | None = None,
    ):
        query = select(User).order_by(User.created_at.desc())
        total = select(func.count()).select_from(User)

        if offset:
            query = query.offset(offset)

        if limit:
            query = query.limit(limit)
        total_res = await session.execute(total)
        result = await session.execute(query)
        return total_res.scalars().first(), result.scalars().all()

    @Transactional()
    async def create_user(self, phone_number: str, username: str, session: AsyncSession, **kwargs) -> User:
        try:
            query = select(User).where(or_(User.phone_number == phone_number, User.username == username))
            result = await session.execute(query)
            is_exist = result.scalars().first()
            if is_exist:
                raise DuplicatePhoneNumberOrUsernameException

            user = User(phone_number=phone_number, username=username, **kwargs)  # type: ignore
            session.add(user)
            await session.commit()

            await session.refresh(user)
            return user

        except Exception as e:
            await session.rollback()
            await session.close()
            raise e

    @Transactional()
    async def is_superuser(self, user_id: UUID4, session: AsyncSession) -> bool:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            return False

        if user.is_superuser is False:
            return False

        return True

    @Transactional()
    async def login(self, phone_number: str, session: AsyncSession) -> LoginResponse:
        result = await session.execute(select(User).where(and_(User.phone_number == phone_number)))
        user = result.scalars().first()

        if not user:
            raise UserNotFoundException("User not found")

        response = LoginResponse(
            token=TokenHelper.encode(payload={"user_id": str(user.id)}),
            refresh_token=TokenHelper.encode(payload={"sub": "refresh"}, expire_period=60 * 60 * 24 * 30),
            user_id=user.id,
        )
        return response

    @Transactional()
    async def logout(self, user_id: UUID4, session: AsyncSession) -> None:
        result = await session.execute(select(User).where(User.id == user_id))
        user: User | None = result.scalars().first()
        if not user:
            raise UserNotFoundException("User not found")
        user.fcm_token = None
        await session.commit()


async def delete_user_by_id(user_id: UUID4, session: AsyncSession, bg: BackgroundTasks) -> User:
    user = await get_my_info_by_id(user_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.phone_number:
        bg.add_task(delete_user_in_firebase, user.phone_number)

    await session.delete(user)
    await session.commit()
    return user


def delete_user_in_firebase(phone_number: str):
    from firebase_admin import auth
    from firebase_admin.auth import UserRecord

    internat_phone_number = f"+82{phone_number[1:]}"
    try:
        fb_user: UserRecord = auth.get_user_by_phone_number(internat_phone_number)
        logger.info(f"Successfully fetched user data: {fb_user.uid}")
        auth.delete_user(fb_user.uid)
    except Exception as e:
        logger.debug(e)


async def update_my_profile_pic_by_id(user_id: UUID4, profile_pic: str, session: AsyncSession) -> User:
    user = await get_my_info_by_id(user_id, session)

    # Update the profile picture URL
    user.profile_pic = profile_pic

    # Add the updated user object to the session and commit the changes
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_my_info_by_id(user_id: UUID4, update_req: UserUpdate, session: AsyncSession) -> User:
    user = await get_my_info_by_id(user_id, session)
    # unsubscribe old fcm token
    if update_req.fcm_token is not None:
        if user.fcm_token != update_req.fcm_token:
            old_fcm_token = user.fcm_token

    for k, v in update_req.update_dict().items():
        if v is not None:
            if k == "gym_info":
                if user.gym_info is not None:
                    if v["address"] == user.gym_info.address:
                        continue

                stmt = select(GymInfo).where(GymInfo.address == v["address"])
                result = await session.execute(stmt)
                db_gym_info: GymInfo | None = result.scalars().first()
                if db_gym_info is None:
                    db_gym_info = GymInfo(**v)
                user.gym_info = db_gym_info
            else:
                print(k, v)
                setattr(user, k, v)

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_my_info_by_id(user_id: UUID4, session: AsyncSession, req_user_id: UUID4 | None = None) -> User:
    is_blocked = False
    if req_user_id is not None:
        is_blocked = await is_blocked_user(session, user_id, req_user_id)

    # if blocked, raise exception
    if is_blocked:
        raise UserBlockedException

    result = await session.execute(select(User).options(selectinload(User.gym_info)).where(User.id == user_id))
    user: User | None = result.scalars().first()
    if not user:
        raise UserNotFoundException
    return user


async def get_random_user_with_limit(db: AsyncSession, user_id: UUID4, limit: int = 3):
    # exclude myself and blocked user
    result = await db.execute(
        select(User.id, User.profile_pic, User.username)
        .order_by(func.random())
        .limit(limit)
        .where(
            User.id != user_id,
            User.id.not_in(select(user_block_list.c.blocked_user_id).where(user_block_list.c.user_id == user_id)),
        )
    )

    out = []

    for row in result.all():
        out.append(row._mapping)
    return out


async def get_others_info_by_id(user_id: UUID4, session: AsyncSession) -> User:
    result = await session.execute(
        select(User).options(selectinload(User.gym_info), raiseload("*")).where(User.id == user_id)
    )
    user: User | None = result.scalars().first()
    if not user:
        raise UserNotFoundException
    return user


async def check_user_phone_number(session: AsyncSession, phone_number: str):
    result = await session.execute(select(User.id).where(User.phone_number == phone_number))
    id: UUID4 | None = result.scalars().first()
    return id is not None


async def check_username(session: AsyncSession, username: str) -> bool:
    result = await session.execute(select(User.id).where(User.username == username))
    id: UUID4 | None = result.scalars().first()
    return id is not None


async def block_user_by_id(
    session: AsyncSession,
    user_id: UUID4,
    block_user_id: UUID4,
) -> bool:
    is_blocked = await is_blocked_user(session, user_id, block_user_id)
    if is_blocked:
        return True
    try:
        await add_block_list(session, user_id, block_user_id)
    except Exception:
        raise UserAlreadyExistsException("User already exists in block list")
    return True


async def get_blocked_users(
    session: AsyncSession,
    user_id: UUID4,
) -> list[User]:
    user = await get_my_info_by_id(user_id, session)
    return user.blocked_users


async def unblock_user_by_id(
    session: AsyncSession,
    user_id: UUID4,
    block_user_id: UUID4,
) -> bool:
    is_blocked = await is_blocked_user(session, user_id, block_user_id)
    if is_blocked:
        try:
            await delete_block_list(session, user_id, block_user_id)
        except Exception as e:
            raise UserNotFoundException("User not found in block list")
    return True


async def get_blocked_me_list(
    session: AsyncSession,
    user_id: UUID4,
) -> set[UUID4]:
    stmt = select(user_block_list.c.user_id).where(user_block_list.c.blocked_user_id == user_id)
    result = await session.execute(stmt)
    blocked_user_ids = result.scalars().all()
    return set(blocked_user_ids)


async def get_my_blocked_list(
    session: AsyncSession,
    user_id: UUID4,
) -> list[Mapping]:
    stmt = select(user_block_list.c.blocked_user_id).where(user_block_list.c.user_id == user_id)
    result = await session.execute(stmt)
    blocked_user_ids: Sequence[UUID4] = result.scalars().all()

    users = await get_minimal_info_by_ids(session, blocked_user_ids)

    return users


async def is_blocked_user(session: AsyncSession, user_id: UUID4, req_user_id: UUID4) -> bool:
    stmt = select(user_block_list).where(
        user_block_list.c.user_id == user_id,
        user_block_list.c.blocked_user_id == req_user_id,
    )
    result = await session.execute(stmt)
    blocked_user = result.scalars().first()
    return blocked_user is not None


async def add_block_list(session: AsyncSession, user_id: UUID4, blocked_user_id: UUID4):
    stmt = insert(user_block_list).values(user_id=user_id, blocked_user_id=blocked_user_id)
    await session.execute(stmt)
    await session.commit()


async def delete_block_list(session: AsyncSession, user_id: UUID4, blocked_user_id: UUID4):
    stmt = delete(user_block_list).where(
        user_block_list.c.user_id == user_id,
        user_block_list.c.blocked_user_id == blocked_user_id,
    )
    await session.execute(stmt)
    await session.commit()


async def get_minimal_info_by_ids(
    session: AsyncSession,
    user_ids: Sequence[UUID4],
):
    result = await session.execute(select(User.id, User.username, User.profile_pic).where(User.id.in_(user_ids)))

    out = result.mappings().all()
    return out
