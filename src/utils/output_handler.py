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