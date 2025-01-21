import json
import os
import subprocess
import tempfile

from .directory_utils import list_non_gitignore_files


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


def apply_ruff(code_action_settings, file_path: str):
    if code_action_settings.get("source.fixAll") == "explicit":
        print("Explicit fix all requested, but not implemented for non-Ruff tools")
        subprocess.run(["ruff", "check", "--fix", file_path], check=False)
    if code_action_settings.get("source.organizeImports") == "explicit":
        print(
            "Explicit organize imports requested, but not implemented for non-Ruff tools"
        )
        # subprocess.run(["ruff", "--select", "I", "--fix", file_path], check=False)
        subprocess.run(["ruff", "format", file_path], check=False)


def apply_linter(file_path: str = None):
    """Apply linter based on .vscode/settings.json"""
    try:
        with open(".vscode/settings.json", "r") as f:
            settings = json.load(f)
    except FileNotFoundError:
        print(".vscode/settings.json not found")
        return
    except json.JSONDecodeError:
        print("Error decoding .vscode/settings.json")
        return

    # Check for Python-related settings
    python_settings = settings.get("[python]", {})
    code_actions = python_settings.get("editor.codeActionsOnSave", {})

    if python_settings.get("editor.formatOnSave"):
        if python_settings.get("editor.defaultFormatter") == "charliermarsh.ruff":
            if file_path:
                apply_ruff(code_actions, file_path)
            else:
                # Apply to all non-gitignored Python files
                for file in list_non_gitignore_files("."):
                    if file.endswith(".py"):
                        apply_ruff(code_actions, file)
        else:
            print(
                f"Default formatter is {python_settings.get('editor.defaultFormatter')}, but not implemented"
            )
