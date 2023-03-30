import aioredis

from app.core.config import settings


def get_redis_url():
    if settings.ENVIRONMENT == "DEV":
        return f"redis://localhost:{settings.REDIS_PORT}"
    return f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"


# singleton redis connection pool
redis = aioredis.from_url(url=get_redis_url())


async def get_redis_conn() -> aioredis.Redis:
    """
    Assemble database URL from self.
    :return: database URL.
    """

    return await aioredis.from_url(url=get_redis_url(), decode_responses=True)
