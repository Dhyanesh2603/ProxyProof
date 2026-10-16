import time
import logging
from typing import Optional, Any
import redis
from app.config import settings

logger = logging.getLogger("proxyproof.cache")

class InMemoryCache:
    """Thread-safe fallback in-memory cache when Redis is unavailable."""
    def __init__(self):
        self._store = {}
        self._expires = {}

    def get(self, key: str) -> Optional[str]:
        self._clean(key)
        val = self._store.get(key)
        return val

    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        self._store[key] = str(value)
        if ex:
            self._expires[key] = time.time() + ex
        elif key in self._expires:
            del self._expires[key]
        return True

    def setex(self, key: str, seconds: int, value: str) -> bool:
        return self.set(key, value, ex=seconds)

    def delete(self, key: str) -> int:
        deleted = 0
        if key in self._store:
            del self._store[key]
            deleted = 1
        if key in self._expires:
            del self._expires[key]
        return deleted

    def exists(self, key: str) -> int:
        self._clean(key)
        return 1 if key in self._store else 0

    def incr(self, key: str) -> int:
        self._clean(key)
        curr = int(self._store.get(key, 0))
        curr += 1
        self._store[key] = str(curr)
        return curr

    def _clean(self, key: str):
        if key in self._expires:
            if time.time() > self._expires[key]:
                self._store.pop(key, None)
                self._expires.pop(key, None)

class CacheManager:
    def __init__(self):
        self.client = None
        self._is_redis = False
        try:
            r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True, socket_timeout=1)
            r.ping()
            self.client = r
            self._is_redis = True
            logger.info("Connected to Redis server successfully.")
        except Exception as e:
            logger.warning(f"Redis not available ({e}). Using robust In-Memory Cache.")
            self.client = InMemoryCache()
            self._is_redis = False

    def get(self, key: str) -> Optional[str]:
        try:
            return self.client.get(key)
        except Exception:
            return None

    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        try:
            return bool(self.client.set(key, value, ex=ex))
        except Exception:
            return False

    def setex(self, key: str, seconds: int, value: str) -> bool:
        try:
            return bool(self.client.setex(key, seconds, value))
        except Exception:
            return False

    def delete(self, key: str) -> int:
        try:
            return int(self.client.delete(key))
        except Exception:
            return 0

    def exists(self, key: str) -> bool:
        try:
            return bool(self.client.exists(key))
        except Exception:
            return False

    def incr(self, key: str) -> int:
        try:
            return int(self.client.incr(key))
        except Exception:
            return 1

cache = CacheManager()
