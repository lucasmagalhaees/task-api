import json
from unittest.mock import MagicMock, patch

from app.cache import MemoryCache, RedisCache, build_cache


def _make_redis_cache() -> tuple[RedisCache, MagicMock]:
    mock_client = MagicMock()
    with patch("redis.from_url", return_value=mock_client):
        rc = RedisCache()
    return rc, mock_client


class TestMemoryCache:
    def test_miss(self):
        c = MemoryCache()
        assert c.get(1) is None

    def test_set_and_get(self):
        c = MemoryCache()
        c.set(1, {"id": 1, "title": "Test"})
        assert c.get(1) == {"id": 1, "title": "Test"}

    def test_expired(self):
        c = MemoryCache()
        c._store[1] = ({"id": 1}, 0.0)  # timestamp at epoch — always expired
        assert c.get(1) is None

    def test_delete(self):
        c = MemoryCache()
        c.set(1, {"id": 1})
        c.delete(1)
        assert c.get(1) is None

    def test_delete_missing_key(self):
        c = MemoryCache()
        c.delete(999)  # must not raise

    def test_clear(self):
        c = MemoryCache()
        c.set(1, {"id": 1})
        c.set(2, {"id": 2})
        c.clear()
        assert c.get(1) is None
        assert c.get(2) is None


class TestRedisCache:
    def test_get_hit(self):
        rc, mock_client = _make_redis_cache()
        mock_client.get.return_value = b'{"id": 1, "title": "Test"}'
        assert rc.get(1) == {"id": 1, "title": "Test"}
        mock_client.get.assert_called_once_with("task:1")

    def test_get_miss(self):
        rc, mock_client = _make_redis_cache()
        mock_client.get.return_value = None
        assert rc.get(1) is None

    def test_set(self):
        rc, mock_client = _make_redis_cache()
        rc.set(1, {"id": 1, "title": "Test"})
        mock_client.setex.assert_called_once_with(
            "task:1", rc._ttl, json.dumps({"id": 1, "title": "Test"})
        )

    def test_delete(self):
        rc, mock_client = _make_redis_cache()
        rc.delete(1)
        mock_client.delete.assert_called_once_with("task:1")

    def test_clear(self):
        rc, mock_client = _make_redis_cache()
        mock_client.scan_iter.return_value = [b"task:1", b"task:2"]
        rc.clear()
        assert mock_client.delete.call_count == 2


class TestBuildCache:
    def test_default_is_memory(self):
        assert isinstance(build_cache(), MemoryCache)

    def test_dev_profile_uses_redis(self, monkeypatch):
        monkeypatch.setenv("APP_PROFILE", "dev")
        with patch("redis.from_url"):
            result = build_cache()
        assert isinstance(result, RedisCache)
