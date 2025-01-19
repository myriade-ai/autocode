import json
import subprocess
import tempfile
import os

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

def apply_linter():
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

    # Apply Ruff settings
    ruff_settings = settings.get("ruff", {})
    if ruff_settings:
        print("Applying Ruff")
        
        if ruff_settings.get("lint.run") == "onSave":
            print("Running Ruff linter")
            subprocess.run(["ruff", "check", "."], check=False)

        if ruff_settings.get("format.on.save"):
            print("Applying Ruff formatter")
            subprocess.run(["ruff", "format", "."], check=False)

        if ruff_settings.get("organizeImports"):
            print("Organizing imports with Ruff")
            subprocess.run(["ruff", "--select", "I", "--fix", "."], check=False)

        if ruff_settings.get("fixAll"):
            print("Applying all Ruff fixes")
            subprocess.run(["ruff", "--fix", "."], check=False)

        print("Ruff applied successfully")
    else:
        print("No Ruff settings found in .vscode/settings.json")

    # Apply other linter settings if needed (e.g., Pylint)
    if python_settings.get("editor.formatOnSave"):
        formatter = python_settings.get("editor.defaultFormatter")
        if formatter == "charliermarsh.ruff":
            print("Default formatter is Ruff, already applied")
        else:
            print(f"Default formatter is {formatter}, but not implemented")

    code_actions = python_settings.get("editor.codeActionsOnSave", {})
    if code_actions.get("source.fixAll") == "explicit":
        print("Explicit fix all requested, but not implemented for non-Ruff tools")
    if code_actions.get("source.organizeImports") == "explicit":
        print("Explicit organize imports requested, but not implemented for non-Ruff tools")
