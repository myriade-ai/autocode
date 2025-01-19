import os
from .directory_utils import list_non_gitignore_files
from .code_editor_utils import apply_linter

def read_file(filename: str, start_line: int = 1, end_line: int = None) -> str:
    """Read a file with line numbers."""
    with open(filename, "r") as f:
        lines = f.read().splitlines()

    end_line = end_line or len(lines)
    display = []
    width = len(str(end_line))
    for i, line in enumerate(lines[start_line - 1 : end_line], start=start_line):
        display.append(f"{str(i).rjust(width)} | {line}")
    return "\n".join(display)

def write_file(filename: str, content: str):
    """Write the entire content to a file."""
    with open(filename, "w") as f:
        f.write(content)
    apply_linter()

def edit_file(
    filename: str,
    line_index_start: int,
    delete_lines_count: int,
    insert_text: str,
) -> str:
    """Delete a range of lines and insert text at the start line.
    Line numbers are 1-indexed.
    """
    with open(filename, "r") as f:
        lines = f.read().splitlines()

    # Convert line numbers to 0-indexed
    line_index_start -= 1
    line_index_end = line_index_start + delete_lines_count

    new_lines = lines[:line_index_start] + [insert_text] + lines[line_index_end:]
    new_content = "\n".join(new_lines)

    # Write the changes to the file
    with open(filename, "w") as f:
        f.write(new_content)

    # Apply linter after editing the file
    apply_linter()

    return new_content

class CodeEditor:
    def __init__(self, directory: str = "."):
        # Add functions
        self.read_file = read_file
        self.write_file = write_file
        self.edit_file = edit_file

        # Initialize directory
        self.directory = directory

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
                        results.append(f"> {os.path.relpath(full_path, self.directory)}")
                        results.extend(matches)
                        results.append("")  # Empty line between files
            except Exception as e:
                print(f"Error reading file {full_path}: {e}")

        return "\n".join(results).rstrip()
