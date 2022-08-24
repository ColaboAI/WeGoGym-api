from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from typing import AsyncGenerator
from sqlalchemy.orm.session import sessionmaker
from app.core import config
from sqlalchemy.orm import declarative_base, DeclarativeMeta


sqlalchemy_database_uri = config.settings.DEFAULT_SQLALCHEMY_DATABASE_URI

async_engine = create_async_engine(sqlalchemy_database_uri, pool_pre_ping=True)
async_session_maker = sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession
)
Base: DeclarativeMeta = declarative_base()


async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# database adapter dep
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
