"""
Metrics collection system for tracking usage, performance, and API statistics.
"""

import time
import threading
from typing import Dict, List, Any, Optional
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from ..config import settings
from ..logger import logger


@dataclass
class APICallMetrics:
    """Metrics for a single API call."""
    provider: str
    operation: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    success: bool = False
    error_message: Optional[str] = None
    prompt_length: Optional[int] = None
    response_length: Optional[int] = None
    cached: bool = False
    rate_limited: bool = False

    def complete(self, success: bool = True, error_message: str = None,
                response_length: int = None) -> None:
        """Mark the API call as completed."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = success
        self.error_message = error_message
        if response_length is not None:
            self.response_length = response_length


@dataclass
class AggregatedMetrics:
    """Aggregated metrics over a time period."""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_duration: float = 0.0
    avg_duration: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    rate_limit_hits: int = 0
    total_prompt_length: int = 0
    total_response_length: int = 0

    def add_call(self, metrics: APICallMetrics) -> None:
        """Add a call to the aggregated metrics."""
        self.total_calls += 1
        if metrics.success:
            self.successful_calls += 1
        else:
            self.failed_calls += 1

        if metrics.duration:
            self.total_duration += metrics.duration

        if metrics.cached:
            self.cache_hits += 1
        else:
            self.cache_misses += 1

        if metrics.rate_limited:
            self.rate_limit_hits += 1

        if metrics.prompt_length:
            self.total_prompt_length += metrics.prompt_length

        if metrics.response_length:
            self.total_response_length += metrics.response_length

        self._update_averages()

    def _update_averages(self) -> None:
        """Update average calculations."""
        if self.total_calls > 0:
            self.avg_duration = self.total_duration / self.total_calls


class MetricsCollector:
    """Collects and manages metrics with multiple storage backends."""

    def __init__(self):
        self.backend_type = settings.cache_backend if settings.cache_backend == "redis" and REDIS_AVAILABLE else "memory"
        self._lock = threading.Lock()
        self._current_metrics: Dict[str, AggregatedMetrics] = defaultdict(AggregatedMetrics)
        self._recent_calls: List[APICallMetrics] = []
        self._max_recent_calls = 1000

        if self.backend_type == "redis":
            try:
                self.redis = redis.from_url(settings.redis_url)
                self.redis.ping()
                logger.info("Metrics collector initialized with Redis backend")
            except Exception as e:
                logger.warning(f"Redis metrics backend failed, using memory: {e}")
                self.backend_type = "memory"
        else:
            logger.info("Metrics collector initialized with memory backend")

    def record_api_call(self, metrics: APICallMetrics) -> None:
        """Record an API call."""
        with self._lock:
            # Add to recent calls (keep only last N)
            self._recent_calls.append(metrics)
            if len(self._recent_calls) > self._max_recent_calls:
                self._recent_calls.pop(0)

            # Update aggregated metrics
            key = f"{metrics.provider}:{metrics.operation}"
            self._current_metrics[key].add_call(metrics)

            # Store in Redis if available
            if self.backend_type == "redis":
                self._store_in_redis(metrics)

        logger.debug(f"Recorded API call: {metrics.provider}:{metrics.operation} "
                    f"({metrics.duration:.2f}s, success={metrics.success})")

    def get_aggregated_metrics(self, provider: str = None, operation: str = None) -> Dict[str, AggregatedMetrics]:
        """Get aggregated metrics, optionally filtered by provider/operation."""
        with self._lock:
            if provider and operation:
                key = f"{provider}:{operation}"
                return {key: self._current_metrics.get(key, AggregatedMetrics())}
            elif provider:
                return {k: v for k, v in self._current_metrics.items() if k.startswith(f"{provider}:")}
            elif operation:
                return {k: v for k, v in self._current_metrics.items() if k.endswith(f":{operation}")}
            else:
                return dict(self._current_metrics)

    def get_recent_calls(self, limit: int = 100) -> List[APICallMetrics]:
        """Get recent API calls."""
        with self._lock:
            return self._recent_calls[-limit:]

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get overall summary statistics."""
        with self._lock:
            total_calls = sum(m.total_calls for m in self._current_metrics.values())
            successful_calls = sum(m.successful_calls for m in self._current_metrics.values())
            total_duration = sum(m.total_duration for m in self._current_metrics.values())

            return {
                "total_calls": total_calls,
                "successful_calls": successful_calls,
                "failed_calls": total_calls - successful_calls,
                "success_rate": successful_calls / total_calls if total_calls > 0 else 0,
                "total_duration": total_duration,
                "avg_duration": total_duration / total_calls if total_calls > 0 else 0,
                "providers": list(set(k.split(":")[0] for k in self._current_metrics.keys())),
                "operations": list(set(k.split(":")[1] for k in self._current_metrics.keys()))
            }

    def _store_in_redis(self, metrics: APICallMetrics) -> None:
        """Store metrics in Redis."""
        try:
            # Store individual call
            call_key = f"metrics:call:{int(metrics.start_time)}:{metrics.provider}:{metrics.operation}"
            call_data = {
                "provider": metrics.provider,
                "operation": metrics.operation,
                "start_time": metrics.start_time,
                "end_time": metrics.end_time,
                "duration": metrics.duration,
                "success": metrics.success,
                "error_message": metrics.error_message,
                "prompt_length": metrics.prompt_length,
                "response_length": metrics.response_length,
                "cached": metrics.cached,
                "rate_limited": metrics.rate_limited
            }

            import json
            self.redis.setex(call_key, 86400, json.dumps(call_data))  # 24 hours

            # Update aggregated counters
            agg_key = f"metrics:agg:{metrics.provider}:{metrics.operation}"
            self.redis.hincrby(agg_key, "total_calls", 1)
            if metrics.success:
                self.redis.hincrby(agg_key, "successful_calls", 1)
            if metrics.duration:
                self.redis.hincrbyfloat(agg_key, "total_duration", metrics.duration)

        except Exception as e:
            logger.error(f"Redis metrics storage error: {e}")

    def reset_metrics(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._current_metrics.clear()
            self._recent_calls.clear()

            if self.backend_type == "redis":
                try:
                    # Clear Redis metrics (be careful with this in production)
                    keys = self.redis.keys("metrics:*")
                    if keys:
                        self.redis.delete(*keys)
                except Exception as e:
                    logger.error(f"Redis metrics reset error: {e}")

        logger.info("Metrics reset")


# Global metrics collector
metrics_collector = MetricsCollector()


def record_api_call(provider: str, operation: str, prompt_length: int = None,
                   cached: bool = False, rate_limited: bool = False) -> 'MetricsContext':
    """Context manager for recording API calls."""
    return MetricsContext(provider, operation, prompt_length, cached, rate_limited)


class MetricsContext:
    """Context manager for API call metrics."""

    def __init__(self, provider: str, operation: str, prompt_length: int = None,
                 cached: bool = False, rate_limited: bool = False):
        self.metrics = APICallMetrics(
            provider=provider,
            operation=operation,
            start_time=time.time(),
            prompt_length=prompt_length,
            cached=cached,
            rate_limited=rate_limited
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        success = exc_type is None
        error_message = str(exc_val) if exc_val else None
        self.metrics.complete(success=success, error_message=error_message)
        metrics_collector.record_api_call(self.metrics)

    def set_response_length(self, length: int) -> None:
        """Set the response length."""
        self.metrics.response_length = length