import uuid
from fastapi import Depends
from fastapi_users import FastAPIUsers
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users.db import SQLAlchemyUserDatabase
from app.models import OAuthAccount, User
from app.core.security import UserManager, auth_backend
from app.session import get_async_session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(
        session=session, user_table=User, oauth_account_table=OAuthAccount
    )


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])
get_current_user = fastapi_users.current_user()
get_current_active_user = fastapi_users.current_user(active=True)
get_current_superuser = fastapi_users.current_user(active=True, superuser=True)
