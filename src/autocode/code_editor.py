from .directory_utils import list_non_gitignore_files


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

    del lines[line_index_start:line_index_end]
    lines.insert(line_index_start, insert_text)

    with open(filename, "w") as f:
        f.write("\n".join(lines))

    return "\n".join(lines)


class CodeEditor:
    def __init__(self, directory: str = "."):
        # Add functions
        self.read_file = read_file
        self.write_file = write_file
        self.edit_file = edit_file

        # Initialize directory
        self.directory = directory

    def search_files(self, search_text: str) -> str:
        """Search recursively for files containing 'search_text' and return results in VSCode format."""
        files = list_non_gitignore_files(self.directory)
        results = []

        for path in files:
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    matches = []
                    for i, line in enumerate(lines, 1):
                        if search_text in line:
                            # Strip whitespace and limit line length if too long
                            line_preview = line.strip()
                            if len(line_preview) > 100:
                                line_preview = line_preview[:97] + "..."
                            matches.append(f"  Line {i}: {line_preview}")

                    if matches:
                        results.append(f"> {path}")
                        results.extend(matches)
                        results.append("")  # Empty line between files
            except Exception:
                pass

        return "\n".join(results).rstrip()

    def __repr__(self):
        return "\n".join(self.files[:10])


if __name__ == "__main__":
    editor = CodeEditor()
    print(editor.search_files("print"))
