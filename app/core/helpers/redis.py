import redis.asyncio as aioredis

from app.core.config import settings

redis = aioredis.from_url(
    url=f"redis://{settings.REDIS_USERNAME}:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
)


async def async_redis_conn(self) -> str:
    """
    Assemble database URL from self.
    :return: database URL.
    """
    return await aioredis.from_url(
        "redis://"
        + settings.REDIS_USERNAME
        + ":"
        + settings.REDIS_PASSWORD
        + "@"
        + settings.REDIS_HOST
        + ":"
        + settings.REDIS_PORT
        + "/"
        "0",
        decode_responses=True,
    )
