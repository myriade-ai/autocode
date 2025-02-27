import os

from PIL import Image

from .code_editor_utils import apply_linter
from .directory_utils import list_non_gitignore_files


class CodeEditor:
    def __init__(self, directory: str = "."):
        self.directory = directory

    def __repr__(self):
        """Currently: display the directory of the code editor."""
        return "Directory:\n" + self.display_directory()

    def read_file(self, filename: str, start_line: int = 1, end_line: int = None):
        """Read a file with line numbers
        If the file is an image, return a base64-encoded image
        """
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            return Image.open(filename)

        with open(filename, "r") as f:
            lines = f.read().splitlines()

        end_line = end_line or len(lines)
        display = []
        width = len(str(end_line))
        for i, line in enumerate(lines[start_line - 1 : end_line], start=start_line):
            display.append(f"{str(i).rjust(width)} | {line}")
        return "\n".join(display)

    def write_file(self, filename: str, content: str):
        """Write the entire content to a file."""
        with open(filename, "w") as f:
            f.write(content)

        apply_linter(filename)

        with open(filename, "r") as f:
            return f.read()

    def delete_file(self, filename: str):
        """Delete a file."""
        os.remove(filename)

    def edit_file(
        self,
        filename: str,
        line_index_start: int,
        delete_lines_count: int,
        insert_text: str = None,
    ) -> str:
        """Delete a range of lines and insert text at the start line.
        Line numbers are 1-indexed.
        Args:
            filename: The path to the file to edit.
            line_index_start: The line number to start deleting from.
            delete_lines_count: The number of lines to delete.
            insert_text: The text to insert at the start line.
        Returns:
            The content of the file after editing.
        """
        with open(filename, "r") as f:
            lines = f.read().splitlines()

        # Convert line numbers to 0-indexed
        line_index_start -= 1
        line_index_end = line_index_start + delete_lines_count

        if insert_text:
            new_lines = (
                lines[:line_index_start] + [insert_text] + lines[line_index_end:]
            )
        else:
            new_lines = lines[:line_index_start] + lines[line_index_end:]
        new_content = "\n".join(new_lines)

        # Write the changes to the file
        with open(filename, "w") as f:
            f.write(new_content)

        # Apply linter after editing the file
        apply_linter(filename)

        with open(filename, "r") as f:
            return f.read()

    def display_directory(self) -> str:
        """Display all the non-gitignored files in the directory."""
        files = list_non_gitignore_files(self.directory)
        return "\n".join(files)

    def search_files(self, search_text: str) -> str:
        """Search recursively for files containing 'search_text' and return results in VSCode format."""
        files = list_non_gitignore_files(self.directory)
        results = []

        for path in files:
            full_path = os.path.join(self.directory, path)
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    matches = []
                    for i, line in enumerate(lines, 1):
                        if search_text.lower() in line.lower():
                            # Strip whitespace and limit line length if too long
                            line_preview = line.strip()
                            if len(line_preview) > 100:
                                line_preview = line_preview[:97] + "..."
                            matches.append(f"  Line {i}: {line_preview}")

                    if matches:
                        results.append(
                            f"> {os.path.relpath(full_path, self.directory)}"
                        )
                        results.extend(matches)
                        results.append("")  # Add a blank line between file results
            except Exception as e:
                print(f"Error reading file {full_path}: {e}")

        if not results:
            return "No files found."

        return "\n".join(results).rstrip()

    # def submit(self):
    #     """Create a branch, run tests, and ask user for a review."""
    #     import subprocess

    #     # Create a new branch
    #     branch_name = f"feature-{int(time.time())}"
    #     subprocess.run(["git", "checkout", "-b", branch_name], check=True)

    #     # Run tests
    #     test_result = subprocess.run(["pytest"], capture_output=True, text=True)

    #     if test_result.returncode != 0:
    #         print("Tests failed. Please fix the issues before submitting.")
    #         print(test_result.stdout)
    #         print(test_result.stderr)
    #         return

    #     # If tests pass, show changes and ask for review
    #     diff = subprocess.run(["git", "diff"], capture_output=True, text=True).stdout
    #     print("Changes to be submitted:")
    #     print(diff)

    #     user_input = input("Do you want to submit these changes? (y/n): ").lower()
    #     if user_input == "y":
    #         # Commit changes
    #         subprocess.run(["git", "add", "."], check=True)
    #         subprocess.run(
    #             ["git", "commit", "-m", f"Feature: {branch_name}"], check=True
    #         )

    #         # Push to remote
    #         subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)
    #         print(f"Changes have been pushed to branch: {branch_name}")
    #     else:
    #         print("Submission cancelled.")

    #     # Switch back to the main branch
    #     subprocess.run(["git", "checkout", "main"], check=True)
