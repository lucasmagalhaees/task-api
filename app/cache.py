import json
import os
import time


class MemoryCache:
    def __init__(self):
        self._ttl = int(os.getenv("CACHE_TTL", "60"))
        self._store: dict[int | str, tuple[dict, float]] = {}

    def get(self, key: int | str) -> dict | None:
        entry = self._store.get(key)
        if entry and time.monotonic() - entry[1] < self._ttl:
            return entry[0]
        return None

    def set(self, key: int | str, value: dict) -> None:
        self._store[key] = (value, time.monotonic())

    def delete(self, key: int | str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()


class RedisCache:
    def __init__(self):
        import redis
        self._ttl = int(os.getenv("CACHE_TTL", "60"))
        self._client = redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379"))

    def get(self, key: int | str) -> dict | None:
        value = self._client.get(f"task:{key}")
        if value:
            return json.loads(value)
        return None

    def set(self, key: int | str, value: dict) -> None:
        self._client.setex(f"task:{key}", self._ttl, json.dumps(value))

    def delete(self, key: int | str) -> None:
        self._client.delete(f"task:{key}")

    def clear(self) -> None:
        for k in self._client.scan_iter("task:*"):
            self._client.delete(k)


def build_cache() -> MemoryCache | RedisCache:
    if os.getenv("APP_PROFILE", "local") == "dev":
        return RedisCache()
    return MemoryCache()


cache = build_cache()
