import hashlib
import json
import logging
import sys
import time

logger = logging.getLogger(__name__)


class CacheService:
    """In-memory LRU cache with size management."""

    def __init__(self, max_items: int = 700, max_size_mb: float = 100):
        self.max_items = max_items
        self.max_size_mb = max_size_mb
        self._store: dict[str, dict] = {}
        self._access_order: list[str] = []

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    @staticmethod
    def make_key(data: dict) -> str:
        """Create a deterministic cache key from a dict."""
        return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def get(self, key: str) -> dict | None:
        """Return cached item or None.  Updates LRU order on hit."""
        if key not in self._store:
            return None
        self._touch(key)
        return self._store[key]

    def put(self, key: str, content: str, media_type: str) -> None:
        """Store content and evict if limits are exceeded."""
        content_size = sys.getsizeof(content)
        self._store[key] = {
            "content": content,
            "media_type": media_type,
            "last_used": time.time(),
            "size": content_size,
        }
        self._touch(key)
        self._evict()
        logger.info(
            "Cache STORE (%s bytes) - %d items, %.2fMB",
            content_size,
            len(self._store),
            self.size_mb,
        )

    def clear(self) -> None:
        self._store.clear()
        self._access_order.clear()

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def size_mb(self) -> float:
        return sum(item["size"] for item in self._store.values()) / (1024 * 1024)

    def info(self) -> dict:
        return {
            "cache_items": len(self._store),
            "cache_size_mb": round(self.size_mb, 2),
            "max_items": self.max_items,
            "max_size_mb": self.max_size_mb,
            "cached_keys": list(self._store.keys()),
            "access_order": list(self._access_order),
        }

    def update_config(self, max_items: int | None, max_size_mb: float | None) -> dict:
        if max_items is not None and max_items > 0:
            self.max_items = max_items
        if max_size_mb is not None and max_size_mb > 0:
            self.max_size_mb = max_size_mb
        self._evict()
        return {
            "message": "Cache configuration updated",
            "max_items": self.max_items,
            "max_size_mb": self.max_size_mb,
            "current_items": len(self._store),
            "current_size_mb": round(self.size_mb, 2),
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _touch(self, key: str) -> None:
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
        if key in self._store:
            self._store[key]["last_used"] = time.time()

    def _evict(self) -> None:
        evicted = 0
        while (
            len(self._store) > self.max_items or self.size_mb > self.max_size_mb
        ) and self._store:
            if self._access_order:
                lru_key = self._access_order.pop(0)
                if lru_key in self._store:
                    del self._store[lru_key]
                    evicted += 1
            else:
                del self._store[next(iter(self._store))]
                evicted += 1
        if evicted:
            logger.info(
                "Cache eviction: removed %d items. Now %d items, %.2fMB",
                evicted,
                len(self._store),
                self.size_mb,
            )
