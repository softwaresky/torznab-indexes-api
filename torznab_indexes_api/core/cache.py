import asyncio
from functools import lru_cache
from cachetools import TTLCache
from typing import Any


class RequestCache:

    def __init__(self, max_requests: int = 10000, request_ttl: int = 600):
        self._cached_requests = TTLCache(maxsize=max_requests,ttl=request_ttl)
        self.lock = asyncio.Lock()

    async def get(self, request_key: str) -> Any:
        async with self.lock:
            return self._cached_requests.get(request_key)

    async def set(self, request_key: str, value: str):
        async with self.lock:
            self._cached_requests[request_key] = value


@lru_cache(maxsize=1)
def get_request_cache() -> RequestCache:
    return RequestCache()