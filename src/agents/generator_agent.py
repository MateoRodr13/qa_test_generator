"""
Legacy AI generator functions - refactored to use new agent system.
"""

from .agent_factory import create_agent
from ..logger import logger

def _build_test_case_prompt(user_story, examples):
    """Build prompt for bilingual test case generation."""

    examples_text = ""
    for i, example in enumerate(examples, 1):
        examples_text += f"\n--- EXAMPLE {i} ---\n"
        examples_text += f"SUMMARY: {example.get('summary', '')}\n"
        for j, step in enumerate(example.get('steps', []), 1):
            examples_text += f"STEP {j}:\n"
            examples_text += f"  ACTION: {step.get('action', '')}\n"
            examples_text += f"  INPUT_DATA: {step.get('input_data', '')}\n"
            examples_text += f"  EXPECTED_RESULT: {step.get('expected_result', '')}\n"

    prompt_template = f"""
Act as an expert QA Analyst. Your task is to analyze the following User Story and generate test cases in both English and Spanish.

Your output MUST be ONLY a single, valid JSON object. Do not include any text, notes, or markdown formatting before or after the JSON object.

The JSON object MUST strictly adhere to the following schema:
{{
  "english_test_cases": [
    {{
      "id": "A unique identifier string for the test case (e.g., TEST-123). REQUIRED.",
      "SUMMARY": "A brief summary of the test case in English. REQUIRED.",
      "STEP 1": {{
        "ACTION": "The action description in English, following Gherkin format. REQUIRED.",
        "INPUT_DATA": "The input data for the step. Can be a string or a JSON object.",
        "EXPECTED_RESULT": "The expected outcome of the step in English. REQUIRED."
      }},
      "STEP 2": {{...}}
    }}
  ],
  "spanish_test_cases": [
    {{
      "id": "A unique identifier string for the test case (e.g., TEST-123). REQUIRED.",
      "SUMMARY": "Un resumen breve del caso de prueba en español. REQUIRED.",
      "STEP 1": {{
        "ACTION": "La descripción de la acción en español, siguiendo el formato Gherkin. REQUIRED.",
        "INPUT_DATA": "Los datos de entrada para el paso. Puede ser una cadena o un objeto JSON.",
        "EXPECTED_RESULT": "El resultado esperado del paso en español. REQUIRED."
      }},
      "STEP 2": {{...}}
    }}
  ]
}}

The 'Action' value in English MUST use the format: 'AS A: [ROLE] I WANT TO: [ACTION]'.
The 'Action' value in Spanish MUST use the format: 'COMO [ROL] QUIERO: [ACCIÓN]'.

---
USER STORY TO ANALYZE:
"{user_story}"

---
HIGH-QUALITY EXAMPLES (Follow this style):
{examples_text}
"""
    return prompt_template

def generate_test_cases(user_story, reference_examples, provider="gemini"):
    """
    Generate test cases using AI agent.
    """
    logger.info(f"Starting test case generation with provider: {provider}")

    agent = create_agent(provider)
    prompt = _build_test_case_prompt(user_story, reference_examples)

    logger.info("Prompt built, sending to AI agent")

    try:
        response = agent.generate_response(prompt)
        if agent.validate_response(response):
            logger.info("Test cases generated successfully")
            return response
        else:
            logger.error("Invalid response from AI agent")
            return None
    except Exception as e:
        logger.error(f"Error generating test cases: {str(e)}")
        return None


def _build_user_story_prompt(description: str) -> str:
    """
    Build prompt for SCRUM user story generation.
    """
    return f"""
You are an Agile Business Analyst and Product Owner expert in SCRUM.

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
- ...
"""


def generate_user_story(description: str, provider="gemini") -> str:
    """
    Generate bilingual SCRUM user story using AI agent.
    """
    logger.info(f"Starting user story generation with provider: {provider}")

    agent = create_agent(provider)
    prompt = _build_user_story_prompt(description)

    logger.info("User story prompt built, sending to AI agent")

    try:
        response = agent.generate_response(prompt)
        if agent.validate_response(response):
            logger.info("User story generated successfully")
            return response
        else:
            logger.error("Invalid response from AI agent")
            return None
    except Exception as e:
        logger.error(f"Error generating user story: {str(e)}")
        return None
