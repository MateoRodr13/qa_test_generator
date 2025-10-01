"""
Enhanced rate limiter with provider-specific limits and Redis support.
"""

import time
from typing import Dict, Optional
from collections import defaultdict

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from ..config import settings
from ..logger import logger


class RateLimiter:
    """Enhanced rate limiter supporting multiple backends and providers."""

    def __init__(self, provider: str = "default", backend: str = "memory"):
        self.provider = provider
        self.backend_type = backend
        self.requests_per_minute = getattr(settings, f"{provider}_requests_per_minute", 60)

        if backend == "redis" and REDIS_AVAILABLE:
            try:
                self.redis = redis.from_url(settings.redis_url)
                self.redis.ping()  # Test connection
                logger.info(f"Redis rate limiter initialized for {provider}")
            except Exception as e:
                logger.warning(f"Redis rate limiter failed for {provider}, falling back to memory: {e}")
                self.backend_type = "memory"
        else:
            self.backend_type = "memory"

        if self.backend_type == "memory":
            self._requests: Dict[str, list] = defaultdict(list)
            logger.info(f"Memory rate limiter initialized for {provider}")

    def is_allowed(self, key: str = "default") -> bool:
        """Check if request is allowed under rate limit."""
        now = time.time()

        if self.backend_type == "redis":
            return self._redis_is_allowed(key, now)
        else:
            return self._memory_is_allowed(key, now)

    def _memory_is_allowed(self, key: str, now: float) -> bool:
        """Memory-based rate limiting."""
        # Clean old requests
        self._requests[key] = [req for req in self._requests[key] if now - req < 60]

        if len(self._requests[key]) < self.requests_per_minute:
            self._requests[key].append(now)
            return True

        logger.warning(f"Rate limit exceeded for {self.provider}:{key}")
        return False

    def _redis_is_allowed(self, key: str, now: float) -> bool:
        """Redis-based rate limiting."""
        try:
            redis_key = f"ratelimit:{self.provider}:{key}"

            # Use Redis sorted set to track requests
            # Add current timestamp
            self.redis.zadd(redis_key, {str(now): now})

            # Remove requests older than 1 minute
            self.redis.zremrangebyscore(redis_key, 0, now - 60)

            # Count remaining requests
            count = self.redis.zcard(redis_key)

            if count <= self.requests_per_minute:
                return True
            else:
                logger.warning(f"Redis rate limit exceeded for {self.provider}:{key}")
                return False

        except Exception as e:
            logger.error(f"Redis rate limiter error: {e}")
            return True  # Allow on error to avoid blocking

    def get_remaining_requests(self, key: str = "default") -> int:
        """Get remaining requests allowed in current window."""
        now = time.time()

        if self.backend_type == "redis":
            try:
                redis_key = f"ratelimit:{self.provider}:{key}"
                self.redis.zremrangebyscore(redis_key, 0, now - 60)
                count = self.redis.zcard(redis_key)
                return max(0, self.requests_per_minute - count)
            except Exception as e:
                logger.error(f"Redis get remaining error: {e}")
                return self.requests_per_minute
        else:
            # Clean old requests
            self._requests[key] = [req for req in self._requests[key] if now - req < 60]
            used = len(self._requests[key])
            return max(0, self.requests_per_minute - used)

    def reset(self, key: str = "default") -> None:
        """Reset rate limit for a key."""
        if self.backend_type == "redis":
            try:
                redis_key = f"ratelimit:{self.provider}:{key}"
                self.redis.delete(redis_key)
                logger.info(f"Redis rate limit reset for {self.provider}:{key}")
            except Exception as e:
                logger.error(f"Redis reset error: {e}")
        else:
            if key in self._requests:
                del self._requests[key]
                logger.info(f"Memory rate limit reset for {self.provider}:{key}")


# Global rate limiters
_rate_limiters: Dict[str, RateLimiter] = {}


def get_rate_limiter(provider: str = "gemini") -> RateLimiter:
    """Get or create a rate limiter for a provider."""
    if provider not in _rate_limiters:
        backend = "redis" if settings.cache_backend == "redis" and REDIS_AVAILABLE else "memory"
        _rate_limiters[provider] = RateLimiter(provider, backend)
    return _rate_limiters[provider]


def rate_limited(provider: str = "gemini"):
    """Decorator for rate limiting."""
    def decorator(func):
        limiter = get_rate_limiter(provider)

        def wrapper(*args, **kwargs):
            if not limiter.is_allowed(func.__name__):
                raise Exception(f"Rate limit exceeded for {provider}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Initialize default rate limiters
_gemini_limiter = get_rate_limiter("gemini")
_openai_limiter = get_rate_limiter("openai")