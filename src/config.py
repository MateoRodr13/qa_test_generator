"""
Configuration management using Pydantic.
Handles API keys, rate limiting, cache settings, and directory paths.
"""

from pydantic import Field
from pydantic_settings import BaseSettings
from pathlib import Path
import os


class Settings(BaseSettings):
    """Application settings with validation."""

    # API Keys
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    openai_api_key: str = Field("", env="OPENAI_API_KEY")  # Optional for now

    # Rate Limiting
    gemini_requests_per_minute: int = Field(60, description="Gemini API rate limit")
    openai_requests_per_minute: int = Field(60, description="OpenAI API rate limit")

    # Cache Settings
    cache_ttl_seconds: int = Field(3600, description="Cache TTL in seconds")
    cache_backend: str = Field("memory", description="Cache backend: memory or redis")

    # Redis (if using)
    redis_url: str = Field("redis://localhost:6379", env="REDIS_URL")

    # Directory Paths
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent)
    data_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "data")
    output_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "output")
    logs_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "logs")

    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_format: str = Field(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # AI Models
    gemini_model: str = Field("gemini-2.5-flash")
    openai_model: str = Field("gpt-4")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.output_dir.mkdir(exist_ok=True)
settings.logs_dir.mkdir(exist_ok=True)

# Update logger with settings if available
try:
    from .logger import logger
    # Reconfigure logger with settings
    logger.info("Applying settings to logger configuration")
except ImportError:
    pass  # Logger not imported yet