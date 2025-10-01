"""
Workflow Manager - Central orchestrator for QA Test Generator workflows.
Coordinates between user story and test case workflows.
"""

from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass

from ..utils.file_handler import load_json_examples, load_user_story_from_txt
from ..cli.interface import cli
from ..logger import logger
from .user_story_workflow import user_story_workflow
from .test_case_workflow import execute_test_case_workflow


class WorkflowState(Enum):
    """States of the workflow execution."""
    INITIALIZED = "initialized"
    USER_STORY_GENERATED = "user_story_generated"
    USER_STORY_ACCEPTED = "user_story_accepted"
    TEST_CASES_GENERATED = "test_cases_generated"
    TEST_CASES_ACCEPTED = "test_cases_accepted"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkflowContext:
    """Context object holding workflow state and data."""
    state: WorkflowState
    user_story_description: Optional[str] = None
    final_user_story: Optional[str] = None
    final_test_cases: Optional[str] = None
    examples_path: Optional[str] = None
    selected_provider: Optional[str] = None
    selected_input_file: Optional[str] = None
    output_dir: str = "output"
    input_filename: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class WorkflowManager:
    """
    Central orchestrator for QA Test Generator workflows.
    Manages the complete flow from input to output generation.
    """

    def __init__(self):
        self.logger = logger.bind(component="workflow_manager")
        self.logger.info("Workflow Manager initialized")

    def execute_complete_workflow(
        self,
        interactive: bool = True,
        default_user_story_path: Optional[str] = None,
        default_examples_path: Optional[str] = None,
        base_output_dir: str = "output"
    ) -> WorkflowContext:
        """
        Execute the complete QA generation workflow.

        Args:
            interactive: Whether to run in interactive mode
            default_user_story_path: Default path to user story file (optional)
            default_examples_path: Default path to examples JSON file (optional)

        Returns:
            WorkflowContext with final results
        """
        context = WorkflowContext(state=WorkflowState.INITIALIZED)

        try:
            self.logger.info("Starting complete workflow execution")

            # Phase 0: Initial selection (interactive mode)
            if interactive:
                if not self._perform_initial_selection(context):
                    context.state = WorkflowState.FAILED
                    return context

                # Create run directory with input filename
                from pathlib import Path
                import os
                from datetime import datetime

                input_path = Path(context.selected_input_file)
                input_name = input_path.stem  # filename without extension
                context.input_filename = input_name

                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                run_dir = os.path.join(base_output_dir, f"run_{timestamp}_{input_name}")
                os.makedirs(run_dir, exist_ok=True)
                context.output_dir = run_dir

            # Set defaults if not selected interactively
            if not context.selected_input_file and default_user_story_path:
                context.selected_input_file = default_user_story_path
                context.input_filename = Path(default_user_story_path).stem
                context.output_dir = base_output_dir  # or create a dir
            if not context.examples_path and default_examples_path:
                context.examples_path = default_examples_path

            # Phase 1: Load and validate input data
            if not self._load_input_data(context):
                context.state = WorkflowState.FAILED
                return context

            # Phase 2: Execute User Story Workflow
            if not self._execute_user_story_workflow(context, interactive):
                context.state = WorkflowState.FAILED
                return context

            # Phase 3: Execute Test Cases Workflow
            if not self._execute_test_cases_workflow(context, interactive):
                context.state = WorkflowState.FAILED
                return context

            # Phase 4: Finalize and report
            self._finalize_workflow(context)
            context.state = WorkflowState.COMPLETED

            self.logger.info("Complete workflow execution finished successfully")
            return context

        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            context.state = WorkflowState.FAILED
            context.metadata['error'] = str(e)
            return context

    def _perform_initial_selection(self, context: WorkflowContext) -> bool:
        """Perform initial user selections for input file and AI provider."""
        try:
            self.logger.info("Performing initial user selections")

            # Select input file
            selected_file = cli.select_input_file()
            if not selected_file:
                cli.display_error("No input file selected")
                return False

            context.selected_input_file = selected_file

            # Select AI provider
            selected_provider = cli.select_ai_provider()
            if not selected_provider:
                cli.display_error("No AI provider selected")
                return False

            context.selected_provider = selected_provider

            self.logger.info(f"Selected input file: {selected_file}")
            self.logger.info(f"Selected AI provider: {selected_provider}")

            return True

        except Exception as e:
            self.logger.error(f"Initial selection failed: {e}")
            return False

    def _load_input_data(self, context: WorkflowContext) -> bool:
        """Load and validate input data."""
        try:
            self.logger.info("Loading input data")

            # Load user story description
            user_story_description = load_user_story_from_txt(context.selected_input_file)
            if not user_story_description:
                cli.display_error("Failed to load user story description")
                return False

            # Load examples (use default path for now)
            from ..config import settings
            examples_path = str(settings.data_dir / "prompt_examples.json")
            examples = load_json_examples(examples_path)
            if not examples:
                cli.display_error("Failed to load examples")
                return False

            context.user_story_description = user_story_description
            context.examples_path = examples_path
            context.metadata['examples_count'] = len(examples)

            cli.display_info(f"Loaded user story description ({len(user_story_description)} characters)")
            cli.display_info(f"Loaded {len(examples)} examples")

            self.logger.info("Input data loaded successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to load input data: {e}")
            return False

    def _execute_user_story_workflow(self, context: WorkflowContext, interactive: bool) -> bool:
        """Execute the user story generation workflow."""
        try:
            self.logger.info("Executing user story workflow")

            if interactive:
                cli.display_info("=== USER STORY WORKFLOW ===")
                final_user_story = user_story_workflow(context.user_story_description, context.selected_provider, context.output_dir, context.input_filename)
            else:
                # Non-interactive mode - generate once
                from ..workflows.user_story_workflow import generate_and_accept_user_story
                final_user_story = generate_and_accept_user_story(context.user_story_description, context.selected_provider, context.output_dir, context.input_filename)

            if not final_user_story:
                cli.display_error("User story generation failed")
                return False

            context.final_user_story = final_user_story
            context.state = WorkflowState.USER_STORY_ACCEPTED

            self.logger.info("User story workflow completed")
            return True

        except Exception as e:
            self.logger.error(f"User story workflow failed: {e}")
            return False

    def _execute_test_cases_workflow(self, context: WorkflowContext, interactive: bool) -> bool:
        """Execute the test cases generation workflow."""
        try:
            self.logger.info("Executing test cases workflow")

            if interactive:
                cli.display_info("=== TEST CASES WORKFLOW ===")
                final_test_cases = execute_test_case_workflow(
                    context.final_user_story,
                    context.examples_path,
                    context.selected_provider,
                    context.output_dir,
                    context.input_filename
                )
            else:
                # Non-interactive mode - generate once
                from ..workflows.test_case_workflow import generate_and_accept_test_cases
                final_test_cases = generate_and_accept_test_cases(
                    context.final_user_story,
                    context.examples_path,
                    context.selected_provider,
                    context.output_dir,
                    context.input_filename
                )

            if not final_test_cases:
                cli.display_error("Test cases generation failed")
                return False

            context.final_test_cases = final_test_cases
            context.state = WorkflowState.TEST_CASES_ACCEPTED

            self.logger.info("Test cases workflow completed")
            return True

        except Exception as e:
            self.logger.error(f"Test cases workflow failed: {e}")
            return False

    def _finalize_workflow(self, context: WorkflowContext):
        """Finalize the workflow and provide summary."""
        try:
            self.logger.info("Finalizing workflow")

            # Display final summary
            cli.display_success("QA Test Generation Complete!")
            cli.display_info("Generated files:")
            if context.input_filename:
                cli.display_info(f"  * User Stories: {context.output_dir}/{context.input_filename}_user_story_*.txt")
                cli.display_info(f"  * Test Cases: {context.output_dir}/{context.input_filename}_test_cases_*.json")
            else:
                cli.display_info(f"  * User Stories: {context.output_dir}/generated_user_story_*.txt")
                cli.display_info(f"  * Test Cases: {context.output_dir}/generated_test_cases_*.json")

            # Update metadata
            context.metadata['completion_time'] = self._get_current_time()
            context.metadata['user_story_length'] = len(context.final_user_story or "")
            context.metadata['test_cases_length'] = len(context.final_test_cases or "")

            self.logger.info("Workflow finalized successfully")

        except Exception as e:
            self.logger.error(f"Workflow finalization failed: {e}")

    def _get_current_time(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def get_workflow_status(self, context: WorkflowContext) -> Dict[str, Any]:
        """Get detailed status of the workflow execution."""
        return {
            'state': context.state.value,
            'has_user_story': bool(context.final_user_story),
            'has_test_cases': bool(context.final_test_cases),
            'metadata': context.metadata,
            'progress': self._calculate_progress(context)
        }

    def _calculate_progress(self, context: WorkflowContext) -> float:
        """Calculate workflow completion percentage."""
        state_progress = {
            WorkflowState.INITIALIZED: 0.0,
            WorkflowState.USER_STORY_GENERATED: 25.0,
            WorkflowState.USER_STORY_ACCEPTED: 50.0,
            WorkflowState.TEST_CASES_GENERATED: 75.0,
            WorkflowState.TEST_CASES_ACCEPTED: 90.0,
            WorkflowState.COMPLETED: 100.0,
            WorkflowState.FAILED: 0.0
        }
        return state_progress.get(context.state, 0.0)