from uuid import UUID
from fastapi import HTTPException

from sqlalchemy import func, or_, select, and_

from app.models import User
from app.models.workout_promise import GymInfo
from app.schemas import LoginResponse
from app.core.exceptions import (
    DuplicatePhoneNumberOrUsernameException,
    UserNotFoundException,
)
from app.schemas.user import UserUpdate
from app.utils.token_helper import TokenHelper
from app.session import transactional_session_factory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

# User service: user adaptor for sqlalchemy
class UserService:
    session: AsyncSession

    def __init__(self):
        self.session_maker = transactional_session_factory

    async def get_user_list(
        self,
        limit: int = 10,
        offset: int | None = None,
    ) -> tuple[int | None, list[User]]:
        self.session: AsyncSession = self.session_maker()
        query = select(User).order_by(User.created_at.desc())
        total = select(func.count()).select_from(User)

        if offset:
            query = query.offset(offset)

        if limit:
            query = query.limit(limit)
        total_res = await self.session.execute(total)
        result = await self.session.execute(query)
        await self.session.close()
        return total_res.scalars().first(), result.scalars().all()

    async def create_user(self, phone_number: str, username: str, **kwargs) -> None:
        try:
            self.session: AsyncSession = self.session_maker()
            query = select(User).where(
                or_(User.phone_number == phone_number, User.username == username)
            )
            result = await self.session.execute(query)
            is_exist = result.scalars().first()
            if is_exist:
                raise DuplicatePhoneNumberOrUsernameException

            user = User(phone_number=phone_number, username=username, **kwargs)
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            await self.session.close()

        except Exception as e:
            await self.session.rollback()
            await self.session.close()
            raise e

    async def is_superuser(self, user_id: UUID) -> bool:
        self.session: AsyncSession = self.session_maker()
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            return False

        if user.is_superuser is False:
            return False

        await self.session.close()
        return True

    async def login(self, phone_number: str) -> LoginResponse:
        self.session: AsyncSession = self.session_maker()
        result = await self.session.execute(
            select(User).where(and_(User.phone_number == phone_number))
        )
        user = result.scalars().first()

        if not user:
            raise UserNotFoundException("User not found")

        response = LoginResponse(
            token=TokenHelper.encode(payload={"user_id": str(user.id)}),
            refresh_token=TokenHelper.encode(
                payload={"sub": "refresh"}, expire_period=60 * 60 * 24 * 30
            ),
        )
        await self.session.close()
        return response


async def delete_user_by_id(user_id: UUID, session: AsyncSession) -> User:
    user = await get_my_info_by_id(user_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await session.delete(user)
    await session.commit()
    return user


async def update_my_info_by_id(
    user_id: UUID, update_req: UserUpdate, session: AsyncSession
) -> User:
    user = await get_my_info_by_id(user_id, session)
    for k, v in update_req.dict(exclude_unset=True).items():
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
                setattr(user, k, v)

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_my_info_by_id(user_id: UUID, session: AsyncSession) -> User:
    result = await session.execute(
        select(User).options(selectinload(User.gym_info)).where(User.id == user_id)
    )
    user: User | None = result.scalars().first()
    if not user:
        raise UserNotFoundException
    return user
