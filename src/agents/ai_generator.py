# src/ai_generator1.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables and configure the API when the module is imported
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please ensure it is set in your .env file or environment.")
genai.configure(api_key=api_key)

# Initialize the model to be ready for use
MODEL = genai.GenerativeModel('gemini-2.5-flash')

def _build_prompt(user_story, examples):
    """Private function to build a more robust final prompt with an explicit schema."""

    # This part remains the same
    examples_text = ""
    for i, example in enumerate(examples, 1):
        # ... (el código para construir examples_text no cambia)
        examples_text += f"\n--- EXAMPLE {i} ---\n"
        examples_text += f"SUMMARY: {example.get('summary', '')}\n"
        for j, step in enumerate(example.get('steps', []), 1):
            examples_text += f"STEP {j}:\n"
            examples_text += f"  ACTION: {step.get('action', '')}\n"
            examples_text += f"  INPUT_DATA: {step.get('input_data', '')}\n"
            examples_text += f"  EXPECTED_RESULT: {step.get('expected_result', '')}\n"

    # --- NEW, STRICTER PROMPT TEMPLATE ---
    prompt_template = f"""
Act as an expert QA Analyst. Your task is to analyze the following User Story and generate test cases.

Your output MUST be ONLY a single, valid JSON object. Do not include any text, notes, or markdown formatting before or after the JSON object.

The JSON object MUST strictly adhere to the following schema:
{{
  "test_cases": [
    {{
      "id": "A unique identifier string for the test case (e.g., TEST-123). REQUIRED.",
      "SUMMARY": "A brief summary of the test case. REQUIRED.",
      "STEP 1": {{
        "ACTION": "The action description, following Gherkin format. REQUIRED.",
        "INPUT_DATA": "The input data for the step. Can be a string or a JSON object.",
        "EXPECTED_RESULT": "The expected outcome of the step. REQUIRED."
      }},
      "STEP 2": {{...}}
    }}
  ]
}}

The 'Action' value MUST use the format: 'AS A: [ROLE] I WANT TO: [ACTION]'.

---
USER STORY TO ANALYZE:
"{user_story}"

---
HIGH-QUALITY EXAMPLES (Follow this style):
{examples_text}
"""
    return prompt_template


def generate_test_cases(user_story, reference_examples):
    """
    Main function that orchestrates the test case generation.
    """
    final_prompt = _build_prompt(user_story, reference_examples)

    print("✅ Prompt built. Sending to the Gemini API...")

    try:
        response = MODEL.generate_content(final_prompt)
        return response.text
    except Exception as e:
        print(f"\n❌ An error occurred while calling the API: {e}")
        return None


def _build_prompt_user_story(description: str) -> str:
    """
    Build a prompt to generate SCRUM User Stories in English and Spanish.
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


def generate_user_story(description: str) -> str:
    """
    Generates a bilingual SCRUM User Story (EN/ES) using Gemini.
    """
    final_prompt = _build_prompt_user_story(description)

    print("✅ Prompt for User Story built. Sending to the Gemini API...")

    try:
        response = MODEL.generate_content(final_prompt)
        return response.text
    except Exception as e:
        print(f"\n❌ An error occurred while calling the API: {e}")
        return None
