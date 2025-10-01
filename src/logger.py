"""
Logging setup using Loguru.
Provides structured logging with console and file outputs.
"""

from loguru import logger
from .config import settings
import sys


def setup_logging():
    """Configure logging with console and file handlers."""

    # Remove default handler
    logger.remove()

    # Console handler with colors
    logger.add(
        sys.stdout,
        format=settings.log_format,
        level=settings.log_level,
        colorize=True,
        backtrace=True,
        diagnose=True
    )

    # File handler for all logs
    logger.add(
        settings.logs_dir / "qa_test_generator.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="1 week",
        encoding="utf-8"
    )

    # File handler for errors only
    logger.add(
        settings.logs_dir / "errors.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="10 MB",
        retention="1 month",
        encoding="utf-8"
    )

    logger.info("Logging setup completed")


# Initialize logging
setup_logging()