"""
Put here any Python code that must be runned before application startup.
It is included in `init.sh` script.

By defualt `main` create a superuser if it does not exist.
"""

import asyncio
from typing import Optional

from sqlalchemy import select
from app.models.user import User
from app.session import get_async_session
import contextlib

from app.api.deps import get_async_session, get_user_db, get_user_manager
from app.schemas import UserCreate
from fastapi_users.exceptions import UserAlreadyExists
from app.core import config as app_config


async def main() -> None:
    print("Start initial data")
    async with get_async_session_context() as session:
        result = await session.execute(
            select(User).where(User.email == app_config.settings.FIRST_SUPERUSER_EMAIL)
        )
        user: Optional[User] = result.scalars().first()

        if user is None:
            await create_user(
                app_config.settings.FIRST_SUPERUSER_EMAIL,
                app_config.settings.FIRST_SUPERUSER_PASSWORD,
                True,
            )
            print("Superuser was created")
        else:
            print("Superuser already exists in database")

        print("Initial data created")


get_async_session_context = contextlib.asynccontextmanager(get_async_session)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


async def create_user(email: str, password: str, is_superuser: bool = False):
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    user = await user_manager.create(
                        UserCreate(
                            email=email, password=password, is_superuser=is_superuser
                        )
                    )
                    print(f"User created {user}")
    except UserAlreadyExists:
        print(f"User {email} already exists")


if __name__ == "__main__":
    asyncio.run(main())
