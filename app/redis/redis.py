from typing import Optional
import aioredis.sentinel
from aioredis import Redis, from_url


class RedisCache:
    def __init__(self):
        self.redis_cache: Optional[Redis] = None

    async def init_cache(self):
        sentinel = aioredis.sentinel.Sentinel(
            [
                ("sentinel-0.sentinel.default.svc.cluster.local", 5000),
                ("sentinel-2.sentinel.default.svc.cluster.local", 5000),
                ("sentinel-1.sentinel.default.svc.cluster.local", 5000),
            ]
        )

        self.redis_cache = sentinel.master_for('mymaster')

    async def keys(self, pattern):
        return await self.redis_cache.keys(pattern)

    async def set(self, key, value):
        return await self.redis_cache.set(key, value)

    async def hset(self, name, mapping):
        return await self.redis_cache.hset(name, mapping=mapping)

    async def hget(self, name, key):
        return await self.redis_cache.hget(name, key)

    async def get(self, key):
        return await self.redis_cache.get(key)

    async def close(self):
        self.redis_cache.close()
        await self.redis_cache.wait_closed()


redis_cache = RedisCache()
