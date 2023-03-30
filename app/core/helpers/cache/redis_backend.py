import pickle
from typing import Any
from fastapi.encoders import jsonable_encoder

import ujson

from app.core.helpers.cache.base import BaseBackend
from app.core.helpers.redis import redis


class RedisBackend(BaseBackend):
    async def get(self, key: str) -> Any:
        result = await redis.get(key)
        if not result:
            return
        try:
            return ujson.loads(result.decode("utf8"))
        except UnicodeDecodeError:
            return pickle.loads(result)

    async def set(self, response: Any, key: str, ttl: int = 60) -> None:
        json_compatible_item_data = jsonable_encoder(response)
        response = ujson.dumps(json_compatible_item_data)
        await redis.set(name=key, value=response, ex=ttl)

    async def delete_startswith(self, value: str) -> None:
        async for key in redis.scan_iter(f"{value}::*"):
            await redis.delete(key)
