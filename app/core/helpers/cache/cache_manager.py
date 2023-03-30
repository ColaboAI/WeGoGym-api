from functools import wraps
from typing import Any

from app.core.helpers.cache.custom_key_maker import CustomKeyMaker

from app.core.helpers.cache.redis_backend import RedisBackend

from .cache_tag import CacheTag
from app.utils.ecs_log import logger


class CacheManager:
    def __init__(self):
        self.backend = None
        self.key_maker = None

    def init(self, backend: RedisBackend, key_maker: CustomKeyMaker) -> None:
        self.backend = backend
        self.key_maker = key_maker

    def cached(
        self,
        prefix: str | None = None,
        tag: CacheTag | None = None,
        ttl: int = 60,
    ):
        def _cached(function):
            @wraps(function)
            async def __cached(*args, **kwargs):
                if not self.backend or not self.key_maker:
                    raise Exception("backend or key_maker is None")
                pf = prefix if prefix else tag.value if tag else None
                ignore_arg_types = []
                key = await self.key_maker.make(
                    pf,
                    ignore_arg_types,
                    function,
                    *args,
                    **kwargs,
                )

                cached_response = await self.backend.get(key=key)
                if cached_response:
                    logger.debug(f"cache hit with redis_key: {key}")
                    return cached_response
                response = await function(*args, **kwargs)
                logger.debug(f"cache miss with redis_key: {key}")
                await self.backend.set(response=response, key=key, ttl=ttl)
                return response

            return __cached

        return _cached

    async def remove_by_tag(self, tag: CacheTag) -> None:
        await self.backend.delete_startswith(value=tag.value)

    async def remove_by_prefix(self, prefix: str) -> None:
        await self.backend.delete_startswith(value=prefix)


Cache = CacheManager()
