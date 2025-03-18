import json
import logging
import os
import subprocess
import tempfile
from typing import Optional

logger = logging.getLogger(__name__)


def apply_diff(diff_text: str):
    """Apply a diff to the file and return the new content and affected lines."""
    # FIX: diff_text should end with a newline
    if not diff_text.endswith("\n"):
        diff_text += "\n"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".patch", delete=False) as f:
        diff_file = f.name
        f.write(diff_text)

    # Apply the patch using git
    try:
        result = subprocess.run(
            ["git", "apply", diff_file],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        return e.stderr
    finally:
        # Clean up temporary files
        os.unlink(diff_file)

    # Apply linter after applying the diff
    apply_linter()
    return result.stdout


def apply_ruff_formatter(file_path: Optional[str] = None):
    if not file_path:
        file_path = "."
    result = subprocess.run(
        ["ruff", "format", file_path], capture_output=True, text=True
    )
    return result.stdout + result.stderr


def apply_ruff_linter(
    file_path: Optional[str] = None, code_action_settings: Optional[dict] = None
):
    if not file_path:
        file_path = "."

    if not code_action_settings:
        code_action_settings = {}

    commands = ["ruff", "check"]

    # Add --fix flag if source.fixAll is explicit
    if code_action_settings.get("source.fixAll") == "explicit":
        commands.append("--fix")

    # Add --select I for imports if source.organizeImports is explicit
    if code_action_settings.get("source.organizeImports") == "explicit":
        commands.extend(["--select", "I"])

    commands.append(file_path)

    result = subprocess.run(
        commands,
        capture_output=True,
        text=True,
    )
    return result.stdout + result.stderr


def apply_linter(file_path: str = None):
    """Apply linter based on .vscode/settings.json"""
    try:
        with open(".vscode/settings.json", "r") as f:
            settings = json.load(f)
    except FileNotFoundError:
        logger.warning(".vscode/settings.json not found")
        return
    except json.JSONDecodeError:
        logger.error("Error decoding .vscode/settings.json")
        return

    # Check for Python-related settings
    python_settings = settings.get("[python]", {})

    # If file is .py
    if file_path.endswith(".py"):
        default_formatter = python_settings.get("editor.defaultFormatter")
        if default_formatter == "charliermarsh.ruff":
            # Formatter
            if python_settings.get("editor.formatOnSave"):
                apply_ruff_formatter(file_path)

            # Linter
            code_actions = python_settings.get("editor.codeActionsOnSave", {})
            if code_actions:
                apply_ruff_linter(file_path, code_actions)
        else:
            logger.warning(
                f"Default formatter is {default_formatter}, but not implemented"
            )
