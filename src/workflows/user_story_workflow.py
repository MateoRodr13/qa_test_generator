"""
User Story interactive workflow.
Handles generation, acceptance, modification, and regeneration.
"""

import os
from ..agents.generator_agent import generate_user_story
from ..utils.output_handler import save_user_story_to_files
from ..cli.interface import cli
from ..logger import logger


def user_story_workflow(initial_description: str, provider: str = "gemini", output_dir: str = "output", input_filename: str = "") -> str:
    """
    Complete interactive workflow for user story generation and modification.

    Returns the final accepted user story.
    """
    logger.info("Starting user story workflow")

    while True:
        # Generate user story
        cli.display_info("Generating User Story...")
        user_story = generate_user_story(initial_description, provider)

        if not user_story:
            cli.display_error("Failed to generate user story")
            return None

        # Display user story
        cli.display_user_story(user_story)

        # Ask for acceptance
        if cli.ask_user_story_acceptance():
            cli.display_success("User Story accepted!")
            # Save final user story
            filename = f"{input_filename}_user_story.txt" if input_filename else "generated_user_story.txt"
            save_user_story_to_files(user_story, os.path.join(output_dir, filename))
            logger.info("User story workflow completed - accepted")
            return user_story
        else:
            action = cli.ask_user_story_action()

            if action == "regenerate":
                cli.display_info("Regenerating User Story...")
                continue  # Loop back to generate again
            else:  # edit
                cli.display_info("Proceeding to edit User Story...")

                # Save for modification
                mod_filename = f"{input_filename}_user_story_for_modification.txt" if input_filename else "user_story_for_modification.txt"
                mod_file = cli.save_for_modification(
                    user_story,
                    os.path.join(output_dir, mod_filename),
                    "User Story for modification"
                )

                # Wait for user modification
                modified_content = cli.wait_for_modification(mod_file)

                if not modified_content.strip():
                    cli.display_error("No modifications found, keeping original")
                    continue

                # Use the edited content directly as the final user story
                cli.display_success("User Story edited and accepted!")
                save_user_story_to_files(modified_content, os.path.join(output_dir, "generated_user_story.txt"))
                logger.info("User story workflow completed - edited")
                return modified_content


def generate_and_accept_user_story(description: str, provider: str = "gemini", output_dir: str = "output", input_filename: str = "") -> str:
    """
    Simplified function for user story generation with acceptance.
    Used when interactive workflow is not needed.
    """
    user_story = generate_user_story(description, provider)
    if user_story:
        filename = f"{input_filename}_user_story.txt" if input_filename else "generated_user_story.txt"
        save_user_story_to_files(user_story, os.path.join(output_dir, filename))
    return user_story