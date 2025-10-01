"""
Base AI Agent class with common functionality.
Includes decorators for retry, rate limiting, and caching.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import time
import hashlib
import json
import logging
from functools import wraps

from ..config import settings
from ..logger import logger
from ..utils.cache import cached
from ..utils.rate_limiter import rate_limited
from ..utils.metrics import record_api_call




def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry on failure with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        sleep_time = delay * (2 ** attempt)
                        logger.warning(f"Attempt {attempt + 1} failed, retrying in {sleep_time}s: {e}")
                        time.sleep(sleep_time)
                    else:
                        logger.error(f"All {max_retries} attempts failed: {e}")
            raise last_exception
        return wrapper
    return decorator


# Rate limiting is now handled by the new rate_limiter module
# The @rate_limited decorator is imported from utils.rate_limiter




class AIAgent(ABC):
    """Abstract base class for AI agents."""

    def __init__(self, provider: str):
        self.provider = provider
        self.logger = logging.getLogger(f'qa_test_generator.{self.__class__.__name__}')

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """Generate response from AI model."""
        pass

    @abstractmethod
    def validate_response(self, response: str) -> bool:
        """Validate the response format."""
        pass

    def log_metrics(self, prompt: str, response: str, duration: float):
        """Log performance metrics using the metrics collector."""
        # This method is kept for backward compatibility but metrics are now
        # automatically collected via the context manager in generate_response
        self.logger.info(
            f"AI call completed - Provider: {self.provider}, "
            f"Prompt length: {len(prompt)}, Response length: {len(response)}, "
            f"Duration: {duration:.2f}s"
        )