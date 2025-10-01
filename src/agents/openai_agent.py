"""
OpenAI Agent implementation.
"""

from openai import OpenAI
import time
from typing import List, Dict, Any

from .base_agent import AIAgent, retry_on_failure, rate_limited, cached
from ..config import settings
from ..logger import logger


class OpenAIAgent(AIAgent):
    """OpenAI agent for generating responses."""

    def __init__(self):
        super().__init__("openai")
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.logger.info("OpenAI agent initialized")

    @retry_on_failure(max_retries=3)
    @rate_limited("openai")
    @cached()
    def generate_response(self, prompt: str) -> str:
        """Generate response using OpenAI API."""
        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7
            )
            result = response.choices[0].message.content

            duration = time.time() - start_time
            self.log_metrics(prompt, result, duration)

            return result

        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise

    def validate_response(self, response: str) -> bool:
        """Basic validation - check if response is not empty."""
        return bool(response and response.strip())


# Factory function
def create_openai_agent():
    """Create and return an OpenAI agent instance."""
    return OpenAIAgent()