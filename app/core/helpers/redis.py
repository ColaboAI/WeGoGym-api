import redis.asyncio as aioredis

from core.config import settings

redis = aioredis.from_url(url=f"redis://{settings.REDIS_HOST}")
