from uuid import UUID

from sqlalchemy import or_, select, and_

from app.models import User
from app.schemas import LoginResponse
from app.core.exceptions import (
    DuplicatePhoneNumberOrUsernameException,
    UserNotFoundException,
)
from app.utils.token_helper import TokenHelper
from app.session import transactional_session_factory
from sqlalchemy.ext.asyncio import AsyncSession

# User service: user adaptor for sqlalchemy
class UserService:
    session: AsyncSession | None = None

    def __init__(self):
        self.session_maker = transactional_session_factory

    async def get_user_list(
        self,
        limit: int = 10,
        prev_id: UUID | None = None,
    ) -> list[User]:
        self.session: AsyncSession = self.session_maker()
        query = select(User).order_by(User.created_at.desc())
        if prev_id:
            query = query.where(User.id < prev_id)

        if limit > 12:
            limit = 12

        query = query.limit(limit)
        result = await self.session.execute(query)
        await self.session.close()
        return result.scalars().all()

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
            raise UserNotFoundException

        response = LoginResponse(
            token=TokenHelper.encode(payload={"user_id": str(user.id)}),
            refresh_token=TokenHelper.encode(payload={"sub": "refresh"}),
        )
        await self.session.close()
        return response
