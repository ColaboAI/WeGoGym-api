from asyncio import current_task
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_scoped_session,
)
from typing import AsyncGenerator
from sqlalchemy.orm.session import sessionmaker
from app.core import config
from sqlalchemy import exc

sqlalchemy_database_uri = config.settings.DEFAULT_SQLALCHEMY_DATABASE_URI
async_engine = create_async_engine(
    sqlalchemy_database_uri, pool_pre_ping=True, echo=True
)

autocommit_engine = async_engine.execution_options(isolation_level="AUTOCOMMIT")
autocommit_session_factory = async_scoped_session(
    sessionmaker(
        autocommit_engine,
        expire_on_commit=False,
        class_=AsyncSession,
        future=True,
    ),
    scopefunc=current_task,
)
transactional_session_factory = async_scoped_session(
    sessionmaker(
        async_engine,
        expire_on_commit=False,
        class_=AsyncSession,
        future=True,
    ),
    scopefunc=current_task,
)


async def get_db_transactional_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create and get database session.
    :param request: current request.
    :yield: database session.
    """
    session: AsyncSession = transactional_session_factory()

    try:  # noqa: WPS501
        yield session
    except exc.DBAPIError:
        await session.rollback()
    finally:
        await session.commit()
        await session.close()


async def get_db_autocommit_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create and get database session.
    :param request: current request.
    :yield: database session.
    """
    session: AsyncSession = autocommit_session_factory()

    try:  # noqa: WPS501
        yield session
    except exc.DBAPIError:
        await session.rollback()
    finally:
        await session.close()
