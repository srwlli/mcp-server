"""Resource caching for MCP Resources with TTL support."""

import time
import threading
from typing import Any, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ResourceCache:
    """Thread-safe cache for MCP Resources with TTL (time-to-live) support.

    This cache stores resource data with automatic expiration after a configurable
    TTL period. It supports manual invalidation and provides cache hit/miss logging
    for observability.

    Attributes:
        default_ttl: Default time-to-live in seconds (default: 300 = 5 minutes)
    """

    def __init__(self, default_ttl: int = 300):
        """Initialize the resource cache.

        Args:
            default_ttl: Default TTL in seconds (default: 300)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self.default_ttl = default_ttl
        self._hits = 0
        self._misses = 0

        logger.info(f"ResourceCache initialized with default TTL: {default_ttl}s")

    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value if found and not expired, None otherwise
        """
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                logger.debug(f"Cache MISS: {key}")
                return None

            entry = self._cache[key]
            expires_at = entry["expires_at"]

            # Check if expired
            if time.time() > expires_at:
                # Remove expired entry
                del self._cache[key]
                self._misses += 1
                logger.debug(f"Cache MISS (expired): {key}")
                return None

            self._hits += 1
            logger.debug(f"Cache HIT: {key}")
            return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in the cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default_ttl if None)
        """
        if ttl is None:
            ttl = self.default_ttl

        with self._lock:
            expires_at = time.time() + ttl
            self._cache[key] = {
                "value": value,
                "expires_at": expires_at,
                "created_at": datetime.utcnow().isoformat()
            }
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")

    def invalidate(self, key: str) -> bool:
        """Manually invalidate (remove) a cache entry.

        Args:
            key: Cache key to invalidate

        Returns:
            True if entry was removed, False if key not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.info(f"Cache INVALIDATED: {key}")
                return True
            return False

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"Cache CLEARED: {count} entries removed")

    def cleanup_expired(self) -> int:
        """Remove all expired entries from the cache.

        Returns:
            Number of expired entries removed
        """
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, entry in self._cache.items()
                if current_time > entry["expires_at"]
            ]

            for key in expired_keys:
                del self._cache[key]

            if expired_keys:
                logger.info(f"Cache cleanup: {len(expired_keys)} expired entries removed")

            return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            dict: Statistics including hits, misses, size, hit rate
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0.0

            return {
                "hits": self._hits,
                "misses": self._misses,
                "total_requests": total_requests,
                "hit_rate_percent": round(hit_rate, 2),
                "current_size": len(self._cache),
                "default_ttl": self.default_ttl
            }

    def __len__(self) -> int:
        """Get current cache size."""
        with self._lock:
            return len(self._cache)


# Global cache instance (singleton)
_resource_cache: Optional[ResourceCache] = None


def get_resource_cache(ttl: int = 300) -> ResourceCache:
    """Get or create the global resource cache instance.

    Args:
        ttl: Default TTL in seconds (only used on first call)

    Returns:
        ResourceCache: The global cache instance
    """
    global _resource_cache
    if _resource_cache is None:
        _resource_cache = ResourceCache(default_ttl=ttl)
    return _resource_cache
