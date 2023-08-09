from asyncio import current_task
from functools import wraps
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_scoped_session,
)
from typing import AsyncGenerator
from sqlalchemy.orm.session import sessionmaker
from app.core import config
from sqlalchemy import exc
from app.utils.ecs_log import logger

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


class Transactional:
    def __call__(self, func):
        session: AsyncSession = transactional_session_factory()

        @wraps(func)
        async def _transactional(*args, **kwargs):
            try:
                kwargs["session"] = session
                result = await func(*args, **kwargs)
                await session.commit()
                return result
            except Exception as e:
                logger.exception(f"{type(e).__name__} : {str(e)}")
                await session.rollback()
                raise e
            finally:
                await session.close()

        return _transactional
