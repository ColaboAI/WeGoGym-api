import aioredis

from app.core.config import settings


def get_redis_url():
    return settings.REDIS_URL


# singleton redis connection pool
redis = aioredis.from_url(url=get_redis_url())


async def get_redis_conn() -> aioredis.Redis:
    """
    Assemble database URL from self.
    :return: database URL.
    """

    return await aioredis.from_url(url=get_redis_url(), decode_responses=True)
