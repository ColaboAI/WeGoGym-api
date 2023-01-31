from typing import Optional, List
from uuid import UUID

from sqlalchemy import or_, select, and_

from app.models import User
from app.schemas import LoginResponseSchema
from app.session import get_async_session
from app.core.exceptions import (
    DuplicatePhoneNumberOrUsernameException,
    UserNotFoundException,
)
from app.utils.token_helper import TokenHelper


class UserService:
    def __init__(self):
        self.session = get_async_session()

    async def get_user_list(
        self,
        limit: int = 12,
    ) -> List[User]:
        query = select(User)

        if limit > 12:
            limit = 12

        query = query.limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_user(self, phone_number: str, username: str) -> None:
        try:

            query = select(User).where(
                or_(User.phone_number == phone_number, User.username == username)
            )
            result = await self.session.execute(query)
            is_exist = result.scalars().first()
            if is_exist:
                raise DuplicatePhoneNumberOrUsernameException

            user = User(phone_number=phone_number, username=username)
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
        except Exception as e:
            await self.session.rollback()
            raise e

    async def is_superuser(self, user_id: UUID) -> bool:
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            return False

        if user.is_superuser is False:
            return False

        return True

    async def login(self, phone_number: str) -> LoginResponseSchema:
        result = await self.session.execute(
            select(User).where(and_(User.phone_number == phone_number))
        )
        user = result.scalars().first()
        if not user:
            raise UserNotFoundException

        response = LoginResponseSchema(
            token=TokenHelper.encode(payload={"user_id": user.id}),
            refresh_token=TokenHelper.encode(payload={"sub": "refresh"}),
        )
        return response
