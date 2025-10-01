"""
Base prompt class for versioned and reusable prompt templates.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from ..logger import logger


@dataclass
class PromptVersion:
    """Version information for prompts."""
    version: str
    created_at: datetime
    description: str
    changes: str


class BasePrompt(ABC):
    """
    Abstract base class for prompt templates.
    Provides versioning, validation, and rendering capabilities.
    """

    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.current_version = version
        self.versions: Dict[str, PromptVersion] = {}
        self.logger = logger.bind(prompt=self.name)
        self._initialize_versions()

    def _initialize_versions(self):
        """Initialize version history. Override in subclasses."""
        pass

    @abstractmethod
    def render(self, **kwargs) -> str:
        """Render the prompt template with given parameters."""
        pass

    @abstractmethod
    def validate_parameters(self, **kwargs) -> bool:
        """Validate input parameters for the prompt."""
        pass

    def get_template(self, version: Optional[str] = None) -> str:
        """Get the prompt template for a specific version."""
        target_version = version or self.current_version
        if target_version not in self.versions:
            raise ValueError(f"Version {target_version} not found for prompt {self.name}")
        return self._get_template_content(target_version)

    @abstractmethod
    def _get_template_content(self, version: str) -> str:
        """Get the actual template content for a version."""
        pass

    def add_version(self, version: str, description: str, changes: str):
        """Add a new version to the prompt."""
        if version in self.versions:
            raise ValueError(f"Version {version} already exists")

        self.versions[version] = PromptVersion(
            version=version,
            created_at=datetime.now(),
            description=description,
            changes=changes
        )
        self.logger.info(f"Added version {version} to prompt {self.name}")

    def list_versions(self) -> Dict[str, PromptVersion]:
        """List all available versions."""
        return self.versions.copy()

    def get_current_version_info(self) -> PromptVersion:
        """Get information about the current version."""
        return self.versions.get(self.current_version)

    def validate_output(self, output: str) -> bool:
        """Validate the AI output format. Override in subclasses."""
        return bool(output and output.strip())

    def __str__(self) -> str:
        return f"{self.name} v{self.current_version}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name} v{self.current_version}>"