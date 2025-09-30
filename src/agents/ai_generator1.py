# ai_generator1.py
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
    """
    Private function to build the final prompt.
    (The underscore indicates it's for internal use in this module).
    """
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
Act as an expert QA Analyst specializing in functional test case creation. Your task is to analyze the following User Story and generate a comprehensive set of test cases to ensure full coverage, considering positive, negative, and edge-case scenarios.

The 'Action' column MUST strictly follow the Gherkin format using the English keywords: 'AS A: [ROLE] I WANT TO: [ACTION] AND: [ANOTHER ACTION IF NEEDED]'.

The output must be ONLY a valid JSON object containing a list called 'test_cases'. Do not include any text before or after the JSON object.

---
USER STORY TO ANALYZE:
"{user_story}"

---
EXAMPLES OF HOW YOU MUST STRUCTURE THE OUTPUT:
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