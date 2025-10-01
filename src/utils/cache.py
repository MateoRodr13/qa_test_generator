"""
Cache implementation supporting in-memory and Redis backends.
Provides caching functionality for AI responses to reduce API calls.
"""

import hashlib
import json
import time
from typing import Any, Optional, Dict
from abc import ABC, abstractmethod

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from ..config import settings
from ..logger import logger


class CacheBackend(ABC):
    """Abstract base class for cache backends."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int) -> None:
        """Set value in cache with TTL."""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries."""
        pass


class InMemoryCache(CacheBackend):
    """In-memory cache implementation."""

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        logger.info("In-memory cache initialized")

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with TTL check."""
        if key in self._cache:
            entry = self._cache[key]
            if time.time() < entry['expires_at']:
                logger.debug(f"Cache hit for key: {key[:16]}...")
                return entry['value']
            else:
                # Expired, remove it
                del self._cache[key]
        logger.debug(f"Cache miss for key: {key[:16]}...")
        return None

    def set(self, key: str, value: Any, ttl: int) -> None:
        """Set value in cache with TTL."""
        expires_at = time.time() + ttl
        self._cache[key] = {
            'value': value,
            'expires_at': expires_at
        }
        logger.debug(f"Cached value for key: {key[:16]}... (TTL: {ttl}s)")

    def delete(self, key: str) -> None:
        """Delete value from cache."""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Deleted cache key: {key[:16]}...")

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        logger.info("Cache cleared")


class RedisCache(CacheBackend):
    """Redis cache implementation."""

    def __init__(self, url: str = None):
        if not REDIS_AVAILABLE:
            raise ImportError("Redis package not available. Install with: pip install redis")

        self.redis_url = url or settings.redis_url
        try:
            self.client = redis.from_url(self.redis_url)
            # Test connection
            self.client.ping()
            logger.info("Redis cache initialized")
        except redis.ConnectionError as e:
            logger.error(f"Redis connection failed: {e}")
            raise

    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        try:
            value = self.client.get(key)
            if value:
                # Deserialize JSON
                deserialized = json.loads(value.decode('utf-8'))
                logger.debug(f"Redis cache hit for key: {key[:16]}...")
                return deserialized
            logger.debug(f"Redis cache miss for key: {key[:16]}...")
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int) -> None:
        """Set value in Redis cache with TTL."""
        try:
            # Serialize to JSON
            serialized = json.dumps(value, default=str)
            self.client.setex(key, ttl, serialized)
            logger.debug(f"Redis cached value for key: {key[:16]}... (TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"Redis set error: {e}")

    def delete(self, key: str) -> None:
        """Delete value from Redis cache."""
        try:
            self.client.delete(key)
            logger.debug(f"Redis deleted key: {key[:16]}...")
        except Exception as e:
            logger.error(f"Redis delete error: {e}")

    def clear(self) -> None:
        """Clear all Redis cache entries."""
        try:
            self.client.flushdb()
            logger.info("Redis cache cleared")
        except Exception as e:
            logger.error(f"Redis clear error: {e}")


class Cache:
    """Main cache interface with automatic backend selection."""

    def __init__(self):
        self.backend = self._create_backend()
        self.default_ttl = settings.cache_ttl_seconds

    def _create_backend(self) -> CacheBackend:
        """Create appropriate cache backend based on configuration."""
        backend_type = settings.cache_backend.lower()

        if backend_type == "redis":
            try:
                return RedisCache()
            except (ImportError, redis.ConnectionError) as e:
                logger.warning(f"Redis cache failed ({e}), falling back to in-memory")
                return InMemoryCache()
        else:
            return InMemoryCache()

    def _make_key(self, *args, **kwargs) -> str:
        """Create a cache key from arguments."""
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        return self.backend.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        ttl = ttl or self.default_ttl
        self.backend.set(key, value, ttl)

    def delete(self, key: str) -> None:
        """Delete value from cache."""
        self.backend.delete(key)

    def clear(self) -> None:
        """Clear all cache entries."""
        self.backend.clear()

    def cached(self, ttl: Optional[int] = None):
        """Decorator for caching function results."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Skip caching if disabled
                if getattr(settings, 'cache_disabled', False):
                    return func(*args, **kwargs)

                # Create cache key
                cache_key = self._make_key(func.__name__, args, kwargs)

                # Try to get from cache first
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_result

                # Execute function
                result = func(*args, **kwargs)

                # Cache the result
                self.set(cache_key, result, ttl)

                return result
            return wrapper
        return decorator


# Global cache instance
cache = Cache()

# Convenience function for easy caching
def cached(ttl: Optional[int] = None):
    """Convenience decorator for caching."""
    return cache.cached(ttl)