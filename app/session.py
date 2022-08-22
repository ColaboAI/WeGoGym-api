from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm import declarative_base, DeclarativeMeta
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase

from app.schemas.user import OAuthAccount, UserRead

Base: DeclarativeMeta = declarative_base()

from app.core import config

if config.settings.ENVIRONMENT == "PYTEST":
    sqlalchemy_database_uri = config.settings.TEST_SQLALCHEMY_DATABASE_URI
else:
    sqlalchemy_database_uri = config.settings.DEFAULT_SQLALCHEMY_DATABASE_URI

async_engine = create_async_engine(sqlalchemy_database_uri, pool_pre_ping=True)
async_session_maker = sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession
)


async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# database adapter dep
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, UserRead, OAuthAccount)
