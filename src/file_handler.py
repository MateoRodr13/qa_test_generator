# file_handler.py
import json

def load_json_examples(file_path):
    """Loads test case examples from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Example file not found at '{file_path}'")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' is not a valid JSON.")
        return None

def load_user_story_from_txt(file_path):
    """Loads the user story from a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: User story file not found at '{file_path}'")
        return None