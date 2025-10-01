"""
Tests package for QA Test Generator.
Contains unit, integration, and end-to-end tests.
"""

# Test configuration and utilities
import os
import sys
from pathlib import Path

# Add src to path for testing
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Set test environment
os.environ.setdefault("LOG_LEVEL", "WARNING")  # Reduce log noise during tests
os.environ.setdefault("TESTING", "true")

__all__ = []