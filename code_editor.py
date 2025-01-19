import json
import subprocess
from pathlib import Path


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

    def edit_file(
        self,
        filename: str,
        delete_line_start: int,
        delete_line_end: int,
        insert_text: str,
    ):
        """Edit a file by deleting a range of lines and inserting text at a specific line."""
        with open(filename, "r") as file:
            lines = file.read().splitlines()

        # Delete the lines
        del lines[delete_line_start:delete_line_end]

        # Insert the text at the specific line
        lines.insert(delete_line_start, insert_text)

        with open(filename, "w") as file:
            file.write("\n".join(lines))

        # TODO: apply linter
        return "\n".join(lines)

    def search_files(self, search_text: str, directory: str = ".") -> list:
        """
        Search recursively in the provided directory (default current directory)
        for files containing the specified search_text.
        Returns the list of file paths that contain the text.
        """
        files_found = []
        for path in Path(directory).rglob("*"):
            if path.is_file():
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        if search_text in content:
                            files_found.append(str(path))
                except Exception:
                    # If any file can't be read for some reason, skip it
                    pass
        return files_found


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
