import logging
import os

from PIL import Image

from autocode.code_editor_utils import apply_linter
from autocode.directory_utils import list_non_gitignore_files

logger = logging.getLogger(__name__)

output_size_limit = int(os.environ["AUTOCHAT_OUTPUT_SIZE_LIMIT"])
FILE_DISPLAY_HEADERS = ["line number|line content", "---|---"]


class CodeEditor:
    def __init__(self, directory: str = "."):
        self.directory = directory
        self.open_files = set()

    def __repr__(self):
        """Currently: display the directory of the code editor."""
        context = "Directory:\n" + self.display_directory()
        context += "\nOpen files:\n"
        for path in self.open_files:
            try:
                context += f"> {path}\n" + self.read_file(path)
                context += "\n==========\n"
            except Exception as e:
                context += f"> {path}\n"
                context += "File is not a text file\n"
                context += "\n==========\n"
                logger.error(f"Error reading file {path}: {e}")
        return context

    def read_file(self, path: str, start_line: int = 1, end_line: int = None):
        f"""Read a file with line numbers
        If the file is an image, return a base64-encoded image
        The output is limited to {output_size_limit} characters
        Reading a file will open it (and keep it open)
        Args:
            path: The path to the file to read.
            start_line: The line number to start reading from (1-indexed).
            end_line: The line number to end reading at (1-indexed).
        Returns:
            The content of the file with line numbers.
        """
        if path not in self.open_files:
            self.open_files.add(path)

        if path.lower().endswith((".png", ".jpg", ".jpeg")):
            return Image.open(path)

        with open(path, "r") as f:
            lines = f.read().splitlines()

        end_line = end_line or len(lines)
        display = FILE_DISPLAY_HEADERS[:]
        width = len(str(end_line))

        for i, line in enumerate(lines[start_line - 1 : end_line], start=start_line):
            display.append(f"{str(i).rjust(width)}|{line}")
        return "\n".join(display)

    def close_file(self, path: str):
        """Close a file when it is no longer needed (for lighter context usage)"""
        self.open_files.remove(path)

    def close_all_files(self):
        """Close all files"""
        self.open_files.clear()

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
        If the file is not open, it will be opened and kept open.
        Args:
            path: The path to the file to edit.
            old_string: The text to replace (must match exactly, including whitespace and indentation)
            new_string: The new text to insert in place of the old text
        Returns:
            The content of the file after editing.
        """
        if path not in self.open_files:
            self.open_files.add(path)

        with open(path, "r") as f:
            content = f.read()

        if old_string not in content:
            raise ValueError(f"Old string '{old_string}' not found in file '{path}'")

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
        If the file is not open, it will be opened and kept open.
        Args:
            path: The path to the file to edit.
            line_index_start: The line number to start deleting from.
            delete_lines_count: The number of lines to delete.
            insert_text: The text to insert at the start line.
            context_lines: The number of lines of context to include in the return
        Returns:
            The content of the file after editing.
        """
        if path not in self.open_files:
            self.open_files.add(path)

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
        if line_index_start > len(lines):
            raise ValueError("Start line out of bounds.")

        if insert_text:
            new_lines = (
                lines[:line_index_start] + [insert_text] + lines[line_index_end:]
            )
        else:
            new_lines = lines[:line_index_start] + lines[line_index_end:]
        new_content = "\n".join(new_lines)

        # Write the full content to the file
        content_display = self._write_file(path, new_content)

        # Calculate the context window
        CONTEXT_WINDOW_SURROUNDING_LINES = 4
        start_context = len(FILE_DISPLAY_HEADERS) + max(
            line_index_start - CONTEXT_WINDOW_SURROUNDING_LINES, 0
        )
        end_context = len(FILE_DISPLAY_HEADERS) + min(
            line_index_start
            + (len(insert_text.split("\n")) if insert_text else 0)
            + CONTEXT_WINDOW_SURROUNDING_LINES,
            len(content_display),
        )
        return "\n".join(
            FILE_DISPLAY_HEADERS
            + content_display.split("\n")[start_context:end_context]
        )

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
