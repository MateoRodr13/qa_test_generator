# src/output_handler.py
import json
import csv
import uuid
import os
from pathlib import Path


def save_cases_to_csv(ai_response_text, output_path):
    """
    Parses the AI's JSON response and saves the test cases to CSV files.
    Now supports bilingual output (English and Spanish versions).
    """
    print("Processing the AI response...")

    try:
        # Clean the AI response, removing markdown code fences if they exist
        ai_response_text = ai_response_text.strip()
        if ai_response_text.startswith("```json"):
            ai_response_text = ai_response_text[7:]  # Remove ```json
        if ai_response_text.endswith("```"):
            ai_response_text = ai_response_text[:-3]  # Remove ```
        ai_response_text = ai_response_text.strip()

        data = json.loads(ai_response_text)

        # Check if it's bilingual format (has english_test_cases and spanish_test_cases)
        if isinstance(data, dict) and 'english_test_cases' in data and 'spanish_test_cases' in data:
            print("Detected bilingual test cases format")
            return _save_bilingual_test_cases(data, output_path)

        # Fallback to legacy format
        test_case_list = []
        if isinstance(data, dict):
            test_case_list = data.get('test_cases', []) or data.get('test_case', [])
        elif isinstance(data, list):
            test_case_list = data
        else:
            print("⚠️ Warning: The root of the JSON response is not a list or a dictionary with expected keys.")

        if not test_case_list:
            print("⚠️ No test cases were found in the AI's response after processing.")
            print("--- FULL RESPONSE ---")
            print(ai_response_text)
            return False

        # Save single language version
        return _save_single_language_test_cases(test_case_list, output_path)

    except json.JSONDecodeError as e:
        print("ERROR: The response from the AI is not valid JSON.")
        print(f"Details: {e}")
        print("--- FULL RESPONSE ---")
        print(ai_response_text)
        return False


def _save_bilingual_test_cases(data, base_output_path):
    """Save bilingual test cases to separate files."""
    try:
        base_path = Path(base_output_path)
        english_path = base_path.parent / f"{base_path.stem}_en{base_path.suffix}"
        spanish_path = base_path.parent / f"{base_path.stem}_es{base_path.suffix}"

        # Save English version
        success_en = _save_single_language_test_cases(data['english_test_cases'], str(english_path))
        if success_en:
            print(f"OK - English test cases saved to '{english_path}'")

        # Save Spanish version
        success_es = _save_single_language_test_cases(data['spanish_test_cases'], str(spanish_path))
        if success_es:
            print(f"OK - Spanish test cases saved to '{spanish_path}'")

        return success_en and success_es

    except Exception as e:
        print(f"ERROR saving bilingual test cases: {e}")
        return False


def _save_single_language_test_cases(test_case_list, output_path):
    """Save test cases for a single language to CSV."""
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            header = ['Test_ID', 'Summary', 'Step_ID', 'Step_Order', 'Action', 'Input_Data', 'Expected_Result']
            writer.writerow(header)

            for case in test_case_list:
                test_id = case.get('id', f"TEST-AI-{uuid.uuid4().hex[:6].upper()}")
                summary = case.get('SUMMARY', case.get('summary', 'N/A'))

                step_keys = sorted([k for k in case.keys() if k.lower().startswith('step_')],
                                   key=lambda k: int(k.split('_')[1]))

                for i, step_key in enumerate(step_keys, 1):
                    step = case[step_key]
                    step_id = str(uuid.uuid4())
                    step_order = i

                    action = step.get('ACTION', step.get('action', ''))
                    input_data_raw = step.get('INPUT_DATA', step.get('input_data', ''))
                    expected_result = step.get('EXPECTED_RESULT', step.get('expected_result', ''))

                    if isinstance(input_data_raw, dict):
                        input_data = json.dumps(input_data_raw)
                    else:
                        input_data = input_data_raw

                    writer.writerow([test_id, summary, step_id, step_order, action, input_data, expected_result])

        print(f"OK - Success! Test cases were saved to '{output_path}'")
        return True
    except Exception as e:
        print(f"ERROR - An unexpected error occurred while writing the CSV: {e}")
        return False


def save_cases_to_json(ai_response_text, base_output_path):
    """
    Saves the AI's JSON response to JSON files.
    Supports bilingual output (English and Spanish versions).
    """
    try:
        # Clean the AI response, removing markdown code fences if they exist
        ai_response_text = ai_response_text.strip()
        if ai_response_text.startswith("```json"):
            ai_response_text = ai_response_text[7:]  # Remove ```json
        if ai_response_text.endswith("```"):
            ai_response_text = ai_response_text[:-3]  # Remove ```
        ai_response_text = ai_response_text.strip()

        data = json.loads(ai_response_text)

        # Check if it's bilingual format (has english_test_cases and spanish_test_cases)
        if isinstance(data, dict) and 'english_test_cases' in data and 'spanish_test_cases' in data:
            print("Detected bilingual test cases format for JSON")
            return _save_bilingual_test_cases_json(data, base_output_path)

        # Single language version
        with open(base_output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"OK - Test cases JSON saved to '{base_output_path}'")
        return True

    except json.JSONDecodeError as e:
        print(f"ERROR: The response from the AI is not valid JSON. {e}")
        return False
    except Exception as e:
        print(f"ERROR saving JSON: {e}")
        return False


def _save_bilingual_test_cases_json(data, base_output_path):
    """Save bilingual test cases to separate JSON files."""
    try:
        from pathlib import Path
        base_path = Path(base_output_path)
        english_path = base_path.parent / f"{base_path.stem}_en{base_path.suffix}"
        spanish_path = base_path.parent / f"{base_path.stem}_es{base_path.suffix}"

        # Save English version
        with open(english_path, 'w', encoding='utf-8') as f:
            json.dump(data['english_test_cases'], f, indent=2, ensure_ascii=False)
        print(f"OK - English test cases JSON saved to '{english_path}'")

        # Save Spanish version
        with open(spanish_path, 'w', encoding='utf-8') as f:
            json.dump(data['spanish_test_cases'], f, indent=2, ensure_ascii=False)
        print(f"OK - Spanish test cases JSON saved to '{spanish_path}'")

        return True

    except Exception as e:
        print(f"ERROR saving bilingual JSON: {e}")
        return False


def save_user_story_to_files(user_story_text, base_output_path):
    """
    Save bilingual user story to separate text files.
    """
    try:
        base_path = Path(base_output_path)

        # Split the response into English and Spanish versions
        if "SPANISH VERSION" in user_story_text:
            parts = user_story_text.split("SPANISH VERSION")
            english_content = parts[0].strip()
            spanish_content = "SPANISH VERSION" + parts[1].strip()

            # Save English version
            english_path = base_path.parent / f"{base_path.stem}_en{base_path.suffix}"
            with open(english_path, 'w', encoding='utf-8') as f:
                f.write(english_content)
            print(f"OK - English user story saved to '{english_path}'")

            # Save Spanish version
            spanish_path = base_path.parent / f"{base_path.stem}_es{base_path.suffix}"
            with open(spanish_path, 'w', encoding='utf-8') as f:
                f.write(spanish_content)
            print(f"OK - Spanish user story saved to '{spanish_path}'")

            return True
        else:
            # Single language version
            with open(base_output_path, 'w', encoding='utf-8') as f:
                f.write(user_story_text)
            print(f"OK - User story saved to '{base_output_path}'")
            return True

    except Exception as e:
        print(f"ERROR saving user story: {e}")
        return False


def generate_individual_test_files(test_cases_json, output_dir, input_filename=""):
    """
    Generate individual JSON files for each test case containing only the steps.

    Args:
        test_cases_json: JSON string or dict containing test cases
        output_dir: Base output directory
        input_filename: Input filename for naming (optional)

    Returns:
        bool: Success status
    """
    try:
        # Parse the test cases JSON if it's a string
        if isinstance(test_cases_json, str):
            # Clean the response
            test_cases_json = test_cases_json.strip()
            if test_cases_json.startswith("```json"):
                test_cases_json = test_cases_json[7:]
            if test_cases_json.endswith("```"):
                test_cases_json = test_cases_json[:-3]
            test_cases_json = test_cases_json.strip()

            data = json.loads(test_cases_json)
        else:
            data = test_cases_json

        # Create test directory
        test_dir = Path(output_dir) / "test"
        test_dir.mkdir(exist_ok=True)

        files_created = 0

        # Process English test cases
        if isinstance(data, dict) and 'english_test_cases' in data:
            for test_case in data['english_test_cases']:
                test_id = test_case.get('id', f"TEST-{uuid.uuid4().hex[:6].upper()}")
                steps = _extract_steps_from_test_case(test_case)

                if steps:
                    filename = f"{test_id}_en.json"
                    filepath = test_dir / filename
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(steps, f, indent=2, ensure_ascii=False)
                    files_created += 1

        # Process Spanish test cases
        if isinstance(data, dict) and 'spanish_test_cases' in data:
            for test_case in data['spanish_test_cases']:
                test_id = test_case.get('id', f"TEST-{uuid.uuid4().hex[:6].upper()}")
                steps = _extract_steps_from_test_case(test_case)

                if steps:
                    filename = f"{test_id}_es.json"
                    filepath = test_dir / filename
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(steps, f, indent=2, ensure_ascii=False)
                    files_created += 1

        # Handle legacy format (direct array of test cases)
        elif isinstance(data, list):
            for test_case in data:
                test_id = test_case.get('id', f"TEST-{uuid.uuid4().hex[:6].upper()}")
                steps = _extract_steps_from_test_case(test_case)

                if steps:
                    # Assume English for legacy format
                    filename = f"{test_id}_en.json"
                    filepath = test_dir / filename
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(steps, f, indent=2, ensure_ascii=False)
                    files_created += 1

        if files_created > 0:
            print(f"OK - Generated {files_created} individual test case files in '{test_dir}'")
            return True
        else:
            print("WARNING - No test case files were generated")
            return False

    except Exception as e:
        print(f"ERROR generating individual test files: {e}")
        return False


def _extract_steps_from_test_case(test_case):
    """
    Extract and transform steps from a test case.
    Converts all parameter values to alphanumeric strings.

    Args:
        test_case: Test case dictionary

    Returns:
        list: List of step dictionaries with ACTION, DATA, RESULT (all alphanumeric strings)
    """
    steps = []

    # Find all step keys and sort them
    step_keys = sorted([k for k in test_case.keys() if k.upper().startswith('STEP')],
                      key=lambda k: int(''.join(filter(str.isdigit, k))))

    for step_key in step_keys:
        step_data = test_case[step_key]
        if isinstance(step_data, dict):
            # Transform the step data
            action_raw = step_data.get('ACTION', step_data.get('action', ''))
            transformed_step = {
                'ACTION': _format_action_with_line_breaks(action_raw),
                'DATA': _to_alphanumeric_string(step_data.get('INPUT_DATA', step_data.get('input_data', None))),
                'RESULT': _to_alphanumeric_string(step_data.get('EXPECTED_RESULT', step_data.get('expected_result', '')))
            }
            steps.append(transformed_step)

    return steps


def _format_action_with_line_breaks(action_text):
    """
    Format ACTION text by adding line breaks after Gherkin keywords and their colons.

    Args:
        action_text: The action text to format

    Returns:
        str: Formatted action text with line breaks
    """
    if not action_text:
        return ""

    # Convert to string first if it's not already
    action_str = _to_alphanumeric_string(action_text)

    # Add line breaks before I WANT TO and AND keywords (but not AS A)
    import re

    # Replace "I WANT TO: " with "\nI WANT TO: "
    action_str = re.sub(r'\b(I WANT TO:\s+)', r'\n\1', action_str)
    # Replace "AND: " with "\nAND: "
    action_str = re.sub(r'\b(AND:\s+)', r'\n\1', action_str)

    return action_str.strip()


def _to_alphanumeric_string(value):
    """
    Convert any value to an alphanumeric string representation.

    Args:
        value: Any value (string, dict, list, None, etc.)

    Returns:
        str: Alphanumeric string representation
    """
    if value is None:
        return ""

    if isinstance(value, str):
        # Keep strings as-is, but ensure they're clean
        return value.strip()

    if isinstance(value, (int, float)):
        # Convert numbers to string
        return str(value)

    if isinstance(value, dict):
        # Convert dict to a clean alphanumeric string
        # Format: key1:value1, key2:value2
        pairs = []
        for k, v in value.items():
            k_clean = ''.join(c for c in str(k) if c.isalnum() or c in ' _-')
            v_clean = ''.join(c for c in str(v) if c.isalnum() or c in ' _-.,')
            if k_clean and v_clean:
                pairs.append(f"{k_clean}:{v_clean}")
        return ', '.join(pairs)

    if isinstance(value, list):
        # Convert list to comma-separated alphanumeric string
        items = []
        for item in value:
            item_str = _to_alphanumeric_string(item)
            if item_str:
                items.append(item_str)
        return ', '.join(items)

    # For any other type, convert to string and clean
    str_value = str(value)
    return ''.join(c for c in str_value if c.isalnum() or c in ' _-.,')