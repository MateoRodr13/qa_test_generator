# src/output_handler.py
import json
import csv
import uuid


def save_cases_to_csv(ai_response_text, output_path):
    """
    Parses the AI's JSON response and saves the test cases to a CSV file.
    This version is robust and handles multiple JSON root formats.
    """
    print("🔄 Processing the AI response...")

    # Clean the AI response, removing markdown code fences if they exist
    ai_response_text = ai_response_text.strip()[8:-3].strip()

    try:
        data = json.loads(ai_response_text)

        test_case_list = []
        if isinstance(data, dict):
            # If the root is a dictionary, try to get the list with the key 'test_cases' or 'test_case'.
            test_case_list = data.get('test_cases', []) or data.get('test_case', [])
        elif isinstance(data, list):
            # THIS IS THE KEY CHANGE: Directly use the list if the root is a list.
            test_case_list = data
        else:
            print(
                "⚠️ Warning: The root of the JSON response is not a list or a dictionary with a 'test_cases' or 'test_case' key.")

        if not test_case_list:
            print("⚠️ No test cases were found in the AI's response after processing.")
            print("--- FULL RESPONSE ---")
            print(ai_response_text)
            return False
    except json.JSONDecodeError as e:
        print("❌ Error: The response from the AI is not valid JSON.")
        print(f"Details: {e}")
        print("--- FULL RESPONSE ---")
        print(ai_response_text)
        return False

    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            header = ['Test_ID', 'Summary', 'Step_ID', 'Step_Order', 'Action', 'Input_Data', 'Expected_Result']
            writer.writerow(header)

            for case in test_case_list:
                test_id = case.get('id', f"TEST-AI-{uuid.uuid4().hex[:6].upper()}")
                summary = case.get('summary', 'N/A')

                step_keys = sorted([k for k in case.keys() if k.lower().startswith('step_')],
                                   key=lambda k: int(k.split('_')[1]))

                for i, step_key in enumerate(step_keys, 1):
                    step = case[step_key]
                    step_id = str(uuid.uuid4())
                    step_order = i

                    action = step.get('action', '')
                    input_data_raw = step.get('input_data', '')
                    expected_result = step.get('expected_result', '')

                    if isinstance(input_data_raw, dict):
                        input_data = json.dumps(input_data_raw)
                    else:
                        input_data = input_data_raw

                    writer.writerow([test_id, summary, step_id, step_order, action, input_data, expected_result])

        print(f"✅ Success! Test cases were saved to '{output_path}'")
        return True
    except Exception as e:
        print(f"❌ An unexpected error occurred while writing the CSV: {e}")
        return False