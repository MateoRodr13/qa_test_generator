"""
User Story prompt template for bilingual SCRUM user story generation.
"""

from .base_prompt import BasePrompt


class UserStoryPrompt(BasePrompt):
    """Prompt template for generating bilingual SCRUM user stories."""

    def __init__(self):
        super().__init__("user_story", "1.0.0")

    def _initialize_versions(self):
        """Initialize version history."""
        self.add_version(
            "1.0.0",
            "Initial bilingual user story prompt",
            "First implementation with EN/ES support"
        )

    def render(self, description: str) -> str:
        """Render the user story prompt with the given description."""
        if not self.validate_parameters(description=description):
            raise ValueError("Invalid parameters for user story prompt")

        template = self._get_template_content(self.current_version)
        return template.format(description=description)

    def validate_parameters(self, **kwargs) -> bool:
        """Validate input parameters."""
        description = kwargs.get('description', '')
        return bool(description and isinstance(description, str) and len(description.strip()) > 10)

    def _get_template_content(self, version: str) -> str:
        """Get the template content for the specified version."""
        if version == "1.0.0":
            return """You are an Agile Business Analyst and Product Owner expert in SCRUM.

Task:
1. Translate the following input from Spanish to English (without losing context or details).
2. Create a User Story in SCRUM format in English:
    - ID: HU-XX
    - Title
    - User Story (As a..., I want..., So that...)
    - Acceptance Criteria (in Gherkin format Given/When/Then, numbered)
    - Non-functional Criteria
3. Provide the same User Story in Spanish with identical structure.

Input (Spanish):
\"\"\"{description}\"\"\"

Output format:
ENGLISH VERSION
---------------
HU-XX - [Title in English]

User Story
----------
As a [role]
I want [functionality]
So that [benefit]

Acceptance Criteria (Gherkin)
-----------------------------
1. ...
    Given ...
    When ...
    Then ...

Non-functional Criteria
-----------------------
- ...

SPANISH VERSION
---------------
HU-XX - [Título en Español]

User Story
----------
Como [rol]
Quiero [funcionalidad]
Para [beneficio]

Acceptance Criteria (Gherkin)
-----------------------------
1. ...
    Dado ...
    Cuando ...
    Entonces ...

Non-functional Criteria
-----------------------
- ..."""

        raise ValueError(f"Unknown version: {version}")

    def validate_output(self, output: str) -> bool:
        """Validate user story output format."""
        if not output or not output.strip():
            return False

        # Check for required sections
        required_sections = [
            "ENGLISH VERSION",
            "SPANISH VERSION",
            "User Story",
            "Acceptance Criteria",
            "Non-functional Criteria"
        ]

        output_upper = output.upper()
        return all(section.upper() in output_upper for section in required_sections)