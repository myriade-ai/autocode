import logging
import os

from PIL import Image

from .code_editor_utils import apply_linter
from .directory_utils import list_non_gitignore_files

logger = logging.getLogger(__name__)

output_size_limit = int(os.environ["AUTOCHAT_OUTPUT_SIZE_LIMIT"])


class CodeEditor:
    def __init__(self, directory: str = "."):
        self.directory = directory

    def __repr__(self):
        """Currently: display the directory of the code editor."""
        return "Directory:\n" + self.display_directory()

    def read_file(self, path: str, start_line: int = 1, end_line: int = None):
        f"""Read a file with line numbers
        If the file is an image, return a base64-encoded image
        The output is limited to {output_size_limit} characters
        Args:
            path: The path to the file to read.
            start_line: The line number to start reading from (1-indexed).
            end_line: The line number to end reading at (1-indexed).
        Returns:
            The content of the file with line numbers.
        """

        if path.lower().endswith((".png", ".jpg", ".jpeg")):
            return Image.open(path)

        with open(path, "r") as f:
            lines = f.read().splitlines()

        end_line = end_line or len(lines)
        display = ["line number|line content", "---|---"]
        width = len(str(end_line))

        for i, line in enumerate(lines[start_line - 1 : end_line], start=start_line):
            display.append(f"{str(i).rjust(width)}|{line}")
        return "\n".join(display)

    def _write_file(self, path: str, content: str):
        """Write the entire content to a file."""
        with open(path, "w") as f:
            f.write(content)

        apply_linter(path)

        return self.read_file(path)

    def create_file(self, path: str, content: str):
        """Create a new file with the given content."""

        # Work only if the file doesn't exist
        if os.path.exists(path):
            raise FileExistsError(f"File {path} already exists")

        return self._write_file(path, content)

    def delete_file(self, path: str):
        """Delete a file."""
        os.remove(path)

    def str_replace(self, path: str, old_string: str, new_string: str) -> str:
        """Replace all occurrences of 'old_string' with 'new_string' in the file.
        Args:
            path: The path to the file to edit.
            old_string: The text to replace (must match exactly, including whitespace and indentation)
            new_string: The new text to insert in place of the old text
        Returns:
            The content of the file after editing.
        """
        with open(path, "r") as f:
            content = f.read()

        content = content.replace(old_string, new_string)
        return self._write_file(path, content)

    def edit_file(
        self,
        path: str,
        line_index_start: int,
        delete_lines_count: int,
        insert_text: str = None,
    ) -> str:
        """Delete a range of lines and insert text at the start line.
        Line numbers are 1-indexed.
        Args:
            path: The path to the file to edit.
            line_index_start: The line number to start deleting from.
            delete_lines_count: The number of lines to delete.
            insert_text: The text to insert at the start line.
        Returns:
            The content of the file after editing.
        """
        with open(path, "r") as f:
            lines = f.read().splitlines()

        # Convert line numbers to 0-indexed
        line_index_start -= 1
        line_index_end = line_index_start + delete_lines_count

        # Safety checks
        if delete_lines_count < 0:
            raise ValueError("Delete lines count must be positive.")
        if line_index_start < 0:
            raise ValueError("Start line out of bounds.")
        if line_index_end < 0:
            raise ValueError("End line out of bounds.")
        if line_index_start > len(lines):
            raise ValueError("Start line out of bounds.")
        if line_index_end > len(lines):
            raise ValueError("End line out of bounds.")

        if insert_text:
            new_lines = (
                lines[:line_index_start] + [insert_text] + lines[line_index_end:]
            )
        else:
            new_lines = lines[:line_index_start] + lines[line_index_end:]
        new_content = "\n".join(new_lines)

        return self._write_file(path, new_content)

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
                logger.error(f"Error reading file {full_path}: {e}")

        if not results:
            return "No files found."

        return "\n".join(results).rstrip()
