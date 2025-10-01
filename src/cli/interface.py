"""
Interactive CLI interface using Rich for user interactions.
Handles user acceptance, modifications, and regeneration workflows.
"""

from typing import Optional, Tuple
import os
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.columns import Columns
from rich.table import Table
from rich.markdown import Markdown

from ..config import settings
from ..logger import logger
from ..agents.agent_factory import AgentFactory


class InteractiveCLI:
    """Interactive CLI for user workflows."""

    def __init__(self):
        self.console = Console()
        self.logger = logger.bind(cli=True)

    def display_welcome(self):
        """Display welcome message."""
        welcome_text = Text("QA Test Generator - Interactive Mode", style="bold blue")
        self.console.print(Panel(welcome_text, title="Welcome", border_style="blue"))

    def select_input_file(self) -> Optional[str]:
        """Let user select from available input files in data directory."""
        data_dir = settings.data_dir
        txt_files = list(data_dir.glob("*.txt"))

        if not txt_files:
            self.display_error("No .txt files found in data directory")
            return None

        if len(txt_files) == 1:
            # Only one file, use it automatically
            selected_file = txt_files[0]
            self.display_info(f"Using input file: {selected_file.name}")
            return str(selected_file)

        # Multiple files, let user choose
        self.console.print("\n[bold cyan]Available Input Files:[/bold cyan]")

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Index", style="cyan", width=6)
        table.add_column("Filename", style="white", width=30)
        table.add_column("Size", style="yellow", width=10)
        table.add_column("Modified", style="green", width=20)

        for i, file_path in enumerate(txt_files, 1):
            stat = file_path.stat()
            size_kb = f"{stat.st_size / 1024:.1f} KB"
            modified = file_path.stat().st_mtime
            from datetime import datetime
            modified_str = datetime.fromtimestamp(modified).strftime("%Y-%m-%d %H:%M")

            table.add_row(str(i), file_path.name, size_kb, modified_str)

        self.console.print(table)

        while True:
            try:
                choice = Prompt.ask(
                    "\n[bold yellow]Select input file (number or filename)[/bold yellow]",
                    choices=[str(i) for i in range(1, len(txt_files) + 1)] + [f.name for f in txt_files]
                )

                # Handle numeric choice
                if choice.isdigit():
                    index = int(choice) - 1
                    if 0 <= index < len(txt_files):
                        selected_file = txt_files[index]
                        break
                else:
                    # Handle filename choice
                    for file_path in txt_files:
                        if file_path.name == choice:
                            selected_file = file_path
                            break
                    else:
                        continue
                    break

            except KeyboardInterrupt:
                return None

        self.display_info(f"Selected: {selected_file.name}")
        return str(selected_file)

    def select_ai_provider(self) -> str:
        """Let user select AI provider."""
        available_providers = AgentFactory.get_available_providers()

        if len(available_providers) == 1:
            provider = available_providers[0]
            self.display_info(f"Using AI provider: {provider.upper()}")
            return provider

        self.console.print("\n[bold cyan]Available AI Providers:[/bold cyan]")

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Index", style="cyan", width=6)
        table.add_column("Provider", style="white", width=15)
        table.add_column("Model", style="yellow", width=25)
        table.add_column("Status", style="green", width=10)

        for i, provider in enumerate(available_providers, 1):
            if provider == "gemini":
                model = settings.gemini_model
                status = "✅ Ready"
            elif provider == "openai":
                model = settings.openai_model
                status = "✅ Ready"
            else:
                model = "Unknown"
                status = "❌ N/A"

            table.add_row(str(i), provider.upper(), model, status)

        self.console.print(table)

        while True:
            try:
                choice = Prompt.ask(
                    "\n[bold yellow]Select AI provider (number or name)[/bold yellow]",
                    choices=[str(i) for i in range(1, len(available_providers) + 1)] + available_providers
                )

                # Handle numeric choice
                if choice.isdigit():
                    index = int(choice) - 1
                    if 0 <= index < len(available_providers):
                        selected_provider = available_providers[index]
                        break
                else:
                    # Handle name choice
                    if choice.lower() in available_providers:
                        selected_provider = choice.lower()
                        break

            except KeyboardInterrupt:
                # Default to first available
                selected_provider = available_providers[0]
                break

        self.display_info(f"Selected AI provider: {selected_provider.upper()}")
        return selected_provider

    def display_user_story(self, user_story: str, title: str = "Generated User Story") -> None:
        """Display user story in a formatted panel."""
        self.console.print(f"\n[bold green]{title}:[/bold green]")
        self.console.print(Panel(user_story, border_style="green"))

    def ask_user_story_acceptance(self) -> bool:
        """Ask user if they accept the generated user story."""
        return Confirm.ask("\n[bold yellow]Do you accept this User Story?[/bold yellow]")

    def ask_user_story_action(self) -> str:
        """Ask user what to do if user story is not accepted."""
        self.console.print("\n[bold yellow]What would you like to do?[/bold yellow]")
        self.console.print("1. Regenerate User Story")
        self.console.print("2. Edit User Story")

        while True:
            try:
                choice = Prompt.ask(
                    "\n[bold yellow]Select option (1 or 2)[/bold yellow]",
                    choices=["1", "2"]
                )

                if choice == "1":
                    return "regenerate"
                elif choice == "2":
                    return "edit"

            except KeyboardInterrupt:
                return "edit"  # Default to edit

    def display_test_cases(self, test_cases_json: str, title: str = "Generated Test Cases") -> None:
        """Display test cases in a formatted way with summary and detailed views."""
        self.console.print(f"\n[bold cyan]{title}:[/bold cyan]")

        try:
            import json
            data = json.loads(test_cases_json)

            # Display English test cases
            if 'english_test_cases' in data:
                self._display_test_cases_table(data['english_test_cases'], "English Test Cases", "cyan")
                self._display_test_cases_detailed(data['english_test_cases'], "English Test Cases", "cyan")

            # Display Spanish test cases
            if 'spanish_test_cases' in data:
                self._display_test_cases_table(data['spanish_test_cases'], "Spanish Test Cases", "magenta")
                self._display_test_cases_detailed(data['spanish_test_cases'], "Spanish Test Cases", "magenta")

        except json.JSONDecodeError:
            # Fallback to raw display
            self.console.print(Panel(test_cases_json, border_style="cyan"))

    def _display_test_cases_table(self, test_cases: list, title: str, color: str) -> None:
        """Display test cases in a summary table format."""
        table = Table(title=f"[bold {color}]{title}[/bold {color}]", show_header=True, header_style=f"bold {color}")

        table.add_column("ID", style=color, width=15)
        table.add_column("Summary", style=f"{color}", width=50)
        table.add_column("Steps", style=f"{color}", width=30)

        for tc in test_cases[:5]:  # Show first 5
            steps_count = len([k for k in tc.keys() if k.startswith('STEP')])
            table.add_row(
                tc.get('id', 'N/A'),
                tc.get('SUMMARY', 'N/A')[:47] + "..." if len(tc.get('SUMMARY', '')) > 47 else tc.get('SUMMARY', ''),
                f"{steps_count} steps"
            )

        self.console.print(table)

        if len(test_cases) > 5:
            self.console.print(f"[dim]And {len(test_cases) - 5} more test cases...[/dim]")

    def _display_test_cases_detailed(self, test_cases: list, title: str, color: str) -> None:
        """Display detailed test cases with full step content."""
        self.console.print(f"\n[bold {color}]Detailed {title}:[/bold {color}]")

        for i, tc in enumerate(test_cases[:3], 1):  # Show first 3 with full details
            self.console.print(f"\n[bold {color}]Test Case {i}:[/bold {color}]")
            self.console.print(f"[bold]ID:[/bold] {tc.get('id', 'N/A')}")
            self.console.print(f"[bold]Summary:[/bold] {tc.get('SUMMARY', 'N/A')}")

            # Display steps
            step_keys = sorted([k for k in tc.keys() if k.startswith('STEP')],
                             key=lambda k: int(''.join(filter(str.isdigit, k))))

            for step_key in step_keys:
                step = tc[step_key]
                action = step.get('ACTION', step.get('action', 'N/A'))
                input_data = step.get('INPUT_DATA', step.get('input_data', 'N/A'))
                expected = step.get('EXPECTED_RESULT', step.get('expected_result', 'N/A'))

                self.console.print(f"  [dim]{step_key}:[/dim]")
                self.console.print(f"    Action: {action}")
                self.console.print(f"    Input: {input_data}")
                self.console.print(f"    Expected: {expected}")
                self.console.print()

        if len(test_cases) > 3:
            self.console.print(f"[dim]And {len(test_cases) - 3} more test cases...[/dim]")

    def ask_test_cases_acceptance(self) -> bool:
        """Ask user if they accept the generated test cases."""
        return Confirm.ask("\n[bold yellow]Do you accept these Test Cases?[/bold yellow]")

    def ask_test_cases_action(self) -> str:
        """Ask user what to do if test cases are not accepted."""
        self.console.print("\n[bold yellow]What would you like to do?[/bold yellow]")
        self.console.print("1. Regenerate Test Cases")
        self.console.print("2. Edit Test Cases")

        while True:
            try:
                choice = Prompt.ask(
                    "\n[bold yellow]Select option (1 or 2)[/bold yellow]",
                    choices=["1", "2"]
                )

                if choice == "1":
                    return "regenerate"
                elif choice == "2":
                    return "edit"

            except KeyboardInterrupt:
                return "edit"  # Default to edit

    def save_for_modification(self, content: str, filename: str, description: str) -> str:
        """Save content to file for user modification."""
        filepath = settings.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        self.console.print(f"\n[bold green]✓ {description} saved to:[/bold green] {filepath}")
        self.console.print("[yellow]Please edit the file and save your changes.[/yellow]")

        return str(filepath)

    def wait_for_modification(self, filepath: str) -> str:
        """Wait for user to modify file and return new content."""
        input(f"\nPress Enter when you have finished editing {filepath}...")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Error reading modified file: {e}")
            return ""

    def display_success(self, message: str):
        """Display success message."""
        self.console.print(f"\n[bold green]SUCCESS: {message}[/bold green]")

    def display_error(self, message: str):
        """Display error message."""
        self.console.print(f"\n[bold red]ERROR: {message}[/bold red]")

    def display_info(self, message: str):
        """Display info message."""
        self.console.print(f"\n[bold blue]INFO: {message}[/bold blue]")


# Global CLI instance
cli = InteractiveCLI()