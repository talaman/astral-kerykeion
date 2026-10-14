from cache_service import CacheService


def test_default_cache_limits():
    cache = CacheService()

    assert cache.info() == {
        "cache_items": 0,
        "cache_size_mb": 0,
        "max_items": 700,
        "max_size_mb": 10,
    }


def test_default_size_limit_evicts_least_recently_used_content():
    cache = CacheService()
    content = "x" * (6 * 1024 * 1024)

    cache.put("first", content, "image/svg+xml")
    assert cache.get("first") is not None

    cache.put("second", content, "image/svg+xml")

    assert cache.get("first") is None
    assert cache.get("second") is not None
    assert cache.info()["cache_items"] == 1
    assert cache.size_mb <= 10
