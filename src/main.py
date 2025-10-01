# src/main.py
import os
from datetime import datetime
from src.workflows.workflow_manager import WorkflowManager
from src.cli.interface import cli
from src.logger import logger

# Define the paths for input and output files relative to the project root
# This assumes you run the script from the root 'qa_test_generator/' directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

EXAMPLES_PATH = os.path.join(DATA_DIR, "prompt_examples.json")
USER_STORY_PATH = os.path.join(DATA_DIR, "user_story.txt")
USER_STORY_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "generated_user_story.txt")
CSV_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "generated_test_cases.csv")

def main():
    """Main function with complete interactive workflow using WorkflowManager."""
    cli.display_welcome()
    logger.info("Starting AI Test Case Generator - Interactive Mode")

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Initialize Workflow Manager
    workflow_manager = WorkflowManager()

    # Execute complete workflow (with initial selection)
    context = workflow_manager.execute_complete_workflow(interactive=True, base_output_dir=OUTPUT_DIR)

    # Check final status
    if context.state.value == "completed":
        logger.info("Interactive workflow completed successfully")
    else:
        logger.error(f"Workflow failed with state: {context.state.value}")
        if 'error' in context.metadata:
            logger.error(f"Error details: {context.metadata['error']}")

if __name__ == "__main__":
    main()