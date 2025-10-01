"""
Agent Factory for creating AI agents dynamically.
"""

from typing import Optional
from .base_agent import AIAgent
from .gemini_agent import GeminiAgent
from .openai_agent import OpenAIAgent
from ..config import settings
from ..logger import logger


class AgentFactory:
    """Factory for creating AI agents."""

    @staticmethod
    def create_agent(provider: str = "gemini") -> AIAgent:
        """Create an AI agent instance based on provider."""
        provider = provider.lower()

        if provider == "gemini":
            logger.info("Creating Gemini agent")
            return GeminiAgent()
        elif provider == "openai":
            logger.info("Creating OpenAI agent")
            return OpenAIAgent()
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    @staticmethod
    def get_available_providers() -> list:
        """Get list of available AI providers."""
        providers = ["gemini"]
        if settings.openai_api_key:
            providers.append("openai")
        return providers

    @staticmethod
    def get_default_provider() -> str:
        """Get the default AI provider."""
        return "gemini"


# Convenience functions
def create_agent(provider: Optional[str] = None) -> AIAgent:
    """Create an agent with optional provider override."""
    if provider is None:
        provider = AgentFactory.get_default_provider()
    return AgentFactory.create_agent(provider)