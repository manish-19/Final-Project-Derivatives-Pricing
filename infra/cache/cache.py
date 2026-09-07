import json
import time
from abc import ABC, abstractmethod
from config import CACHE_NAMESPACE, REDIS_URL

class Cache(ABC):
    @abstractmethod
    def get(self, key): ...
    @abstractmethod
    def set(self, key, value, ttl): ...
    @abstractmethod
    def delete(self, key): ...

class MemoryCache(Cache):
    def __init__(self):
        self._data = {}
    def get(self, key):
        item = self._data.get(key)
        if not item or item[0] <= time.time():
            self._data.pop(key, None)
            return None
        return item[1]
    def set(self, key, value, ttl):
        self._data[key] = (time.time() + ttl, value)
    def delete(self, key):
        self._data.pop(key, None)

class RedisCache(Cache):
    def __init__(self, url):
        import redis
        self.client = redis.Redis.from_url(url, decode_responses=True)
    def get(self, key):
        raw = self.client.get(key)
        return None if raw is None else json.loads(raw)
    def set(self, key, value, ttl):
        self.client.setex(key, ttl, json.dumps(value, default=str))
    def delete(self, key):
        self.client.delete(key)

def key(kind, *parts):
    return ":".join([CACHE_NAMESPACE, kind, *map(str, parts)])

def build_cache():
    return RedisCache(REDIS_URL) if REDIS_URL else MemoryCache()
