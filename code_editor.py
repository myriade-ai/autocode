import json
import subprocess
import tempfile


class CodeEditor:
    def __init__(self):
        self.files = {}

    def read_file(
        self, filename: str, start_line: int = 1, end_line: int = None
    ) -> str:
        """Read a file with line numbers"""
        with open(filename, "r") as file:
            lines = file.read().splitlines()

        end_line = end_line or len(lines)

        display = []
        max_line_num_width = len(str(end_line))

        for i, line in enumerate(lines[start_line - 1 : end_line], start=start_line):
            line_num = str(i).rjust(max_line_num_width)
            display.append(f"{line_num} | {line}")

        return "\n".join(display)

    def write_file(self, filename: str, content: str):
        """Write to a file. The content should be the whole file content."""
        with open(filename, "w") as file:
            file.write(content)

    def apply_diff(self, diff_text: str):
        """Apply a diff to the file and return the new content and affected lines."""
        # FIX: diff_text should end with a newline
        if not diff_text.endswith("\n"):
            diff_text += "\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".patch", delete=False) as f:
            diff_file = f.name
            f.write(diff_text)

        # print("git diff", diff_file)
        # TODO: it's not perfect because it won't work for non git files
        # Apply the patch using git
        try:
            result = subprocess.run(
                [
                    "git",
                    "apply",
                    diff_file,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            return e.stderr
        finally:
            # Clean up temporary files
            # os.unlink(diff_file)
            pass

        # Apply linter after applying the diff
        # apply_linter() # TODO: fix
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
    python_settings = settings.get("python", {})

    # Apply linter settings
    linter = python_settings.get("linting", {}).get("pylintEnabled", False)
    if linter:
        print("Applying Pylint")
        pylint_command = "pylint ."
        try:
            subprocess.run(pylint_command, shell=True, check=True)
            print("Pylint applied successfully")
        except subprocess.CalledProcessError:
            print("Error applying Pylint")

    # Check for Ruff settings
    ruff_settings = settings.get("ruff", {})
    if ruff_settings:
        print("Ruff settings found, but not implemented yet")
        # TODO: Implement Ruff linting based on settings
