"""
Translation prompt template for content translation tasks.
"""

from .base_prompt import BasePrompt


class TranslationPrompt(BasePrompt):
    """Prompt template for translating content between languages."""

    def __init__(self):
        super().__init__("translation", "1.0.0")

    def _initialize_versions(self):
        """Initialize version history."""
        self.add_version(
            "1.0.0",
            "Initial translation prompt",
            "Basic EN/ES translation support"
        )

    def render(self, text: str, source_lang: str = "es", target_lang: str = "en") -> str:
        """Render the translation prompt."""
        if not self.validate_parameters(text=text, source_lang=source_lang, target_lang=target_lang):
            raise ValueError("Invalid parameters for translation prompt")

        template = self._get_template_content(self.current_version)
        return template.format(
            text=text,
            source_lang=source_lang.upper(),
            target_lang=target_lang.upper()
        )

    def validate_parameters(self, **kwargs) -> bool:
        """Validate input parameters."""
        text = kwargs.get('text', '')
        source_lang = kwargs.get('source_lang', '')
        target_lang = kwargs.get('target_lang', '')

        if not text or not isinstance(text, str):
            return False

        if not source_lang or not target_lang:
            return False

        # Supported languages
        supported_langs = ['en', 'es', 'fr', 'de', 'it', 'pt']
        return (source_lang.lower() in supported_langs and
                target_lang.lower() in supported_langs and
                source_lang.lower() != target_lang.lower())

    def _get_template_content(self, version: str) -> str:
        """Get the template content for the specified version."""
        if version == "1.0.0":
            return """You are a professional translator. Your task is to translate the following text from {source_lang} to {target_lang}.

IMPORTANT: Maintain the original meaning, tone, and technical terminology. Do not add or remove information.

Text to translate:
"{text}"

Translation:"""

        raise ValueError(f"Unknown version: {version}")

    def validate_output(self, output: str) -> bool:
        """Validate translation output."""
        if not output or not output.strip():
            return False

        # Basic validation - should be different from input and reasonable length
        output_clean = output.strip()
        return len(output_clean) > 10 and len(output_clean) < len(output) * 3