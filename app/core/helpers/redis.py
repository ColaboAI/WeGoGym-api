import aioredis

from app.core.config import settings


def get_redis_url():
    return f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"


redis = aioredis.from_url(url=get_redis_url(), decode_responses=True)


async def get_redis_conn() -> aioredis.Redis:
    """
    Assemble database URL from self.
    :return: database URL.
    """

    return await aioredis.from_url(url=get_redis_url(), decode_responses=True)
