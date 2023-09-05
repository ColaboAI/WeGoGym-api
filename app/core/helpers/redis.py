import re
from app.core.config import settings
from coredis import RedisCluster
from coredis.retry import ConstantRetryPolicy

print(settings.REDIS_HOST, settings.REDIS_PORT)
# singleton redis connection pool
redis = RedisCluster(
    startup_nodes=[{"host": settings.REDIS_HOST, "port": int(settings.REDIS_PORT)}],
    skip_full_coverage_check=True,
    connect_timeout=10,
)

chat_redis = RedisCluster(
    startup_nodes=[{"host": settings.REDIS_HOST, "port": int(settings.REDIS_PORT)}],
    skip_full_coverage_check=True,
    decode_responses=True,
)
