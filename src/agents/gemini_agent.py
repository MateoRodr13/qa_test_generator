"""
Gemini AI Agent implementation.
"""

import google.generativeai as genai
import time

from .base_agent import AIAgent, retry_on_failure, rate_limited, cached
from ..config import settings
from ..logger import logger
from ..utils.metrics import record_api_call


class GeminiAgent(AIAgent):
    """Gemini AI agent for generating responses."""

    def __init__(self):
        super().__init__("gemini")
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        self.logger.info("Gemini agent initialized")

    @retry_on_failure(max_retries=3)
    @rate_limited("gemini")
    @cached()
    def generate_response(self, prompt: str) -> str:
        """Generate response using Gemini API."""
        with record_api_call("gemini", "generate_response", prompt_length=len(prompt)) as metrics:
            try:
                response = self.model.generate_content(prompt)
                result = response.text

                # Clean markdown formatting from Gemini responses
                if result:
                    result = self._clean_markdown_formatting(result)

                # Set response length for metrics
                metrics.set_response_length(len(result))

                self.log_metrics(prompt, result, metrics.metrics.duration or 0)

                return result

            except Exception as e:
                self.logger.error(f"Gemini API error: {e}")
                raise

    def validate_response(self, response: str) -> bool:
        """Basic validation - check if response is not empty."""
        return bool(response and response.strip())

    def _clean_markdown_formatting(self, text: str) -> str:
        """Remove markdown code blocks and formatting from Gemini responses."""
        if not text:
            return text

        # Remove markdown code blocks
        import re

        # Remove ```json ... ``` blocks
        text = re.sub(r'```\w*\n?', '', text)
        text = re.sub(r'```', '', text)

        # Remove leading/trailing whitespace
        text = text.strip()

        return text


# Factory function for backwards compatibility
def create_gemini_agent():
    """Create and return a Gemini agent instance."""
    return GeminiAgent()