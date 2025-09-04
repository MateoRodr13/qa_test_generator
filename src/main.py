# src/main.py
import os
from file_handler import load_json_examples, load_user_story_from_txt
from ai_generator2 import generate_test_cases
from output_handler import save_cases_to_csv

# Define the paths for input and output files relative to the project root
# This assumes you run the script from the root 'qa_test_generator/' directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

EXAMPLES_PATH = os.path.join(DATA_DIR, "prompt_examples.json")
USER_STORY_PATH = os.path.join(DATA_DIR, "user_story.txt")
CSV_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "generated_test_cases.csv")

def main():
    """Main function of the program."""
    print("--- Starting AI Test Case Generator ---")

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Load data from files
    examples = load_json_examples(EXAMPLES_PATH)
    user_story = load_user_story_from_txt(USER_STORY_PATH)

    if not examples or not user_story:
        print("--- Process stopped due to errors loading files. ---")
        return

    # 2. Call the AI generator to get the response
    ai_response = generate_test_cases(user_story, examples)

    # 3. Process and save the response to a CSV file
    if ai_response:
        print("\n--- RAW RESPONSE RECEIVED FROM AI ---")
        print(ai_response)
        save_cases_to_csv(ai_response, CSV_OUTPUT_PATH)
    else:
        print("\n--- NO RESPONSE RECEIVED FROM AI ---")

    print("\n--- Process finished. ---")

if __name__ == "__main__":
    main()