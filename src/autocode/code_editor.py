from pathlib import Path


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
    delete_line_start: int,
    delete_line_end: int,
    insert_text: str,
) -> str:
    """Delete a range of lines and insert text at the start line."""
    with open(filename, "r") as f:
        lines = f.read().splitlines()

    del lines[delete_line_start:delete_line_end]
    lines.insert(delete_line_start, insert_text)

    with open(filename, "w") as f:
        f.write("\n".join(lines))

    return "\n".join(lines)


def search_files(search_text: str, directory: str = ".") -> list:
    """Search recursively for files containing 'search_text'."""
    results = []
    for path in Path(directory).rglob("*"):
        if path.is_file():
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    if search_text in f.read():
                        results.append(str(path))
            except Exception:
                pass
    return results


class CodeEditor:
    def __init__(self, directory: str = "."):
        # Add functions
        self.read_file = read_file
        self.write_file = write_file
        self.edit_file = edit_file
        self.search_files = search_files

        # Initialize directory
        self.directory = directory
        gitignore_path = Path(directory) / ".gitignore"
        self.ignored_patterns = []

        # Read .gitignore patterns
        if gitignore_path.exists():
            with open(gitignore_path) as f:
                for raw_line in f:
                    line = raw_line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith("#"):
                        continue

                    # If it ends with '/', treat it as a directory pattern
                    if line.endswith("/"):
                        line += "**"  # e.g. ".venv/" -> ".venv/**"

                    # If pattern starts with '/', remove it to make it relative
                    if line.startswith("/"):
                        line = line[1:]

                    # Always store the pattern as-is
                    self.ignored_patterns.append(line)
                    # Also store a variant with '**/' in case we need deeper matching
                    self.ignored_patterns.append(f"**/{line}")

        # Collect all files under the directory
        all_files = [p for p in Path(directory).rglob("*") if p.is_file()]

        self.files = []
        for file_path in all_files:
            # Convert to a relative path (using posix format for consistency)
            rel_path = file_path.relative_to(directory).as_posix()

            # If it starts with '.', remove that leading '.' to avoid mismatches
            # e.g.: ".venv/bin/activate.bat" -> "venv/bin/activate.bat"
            if rel_path.startswith("."):
                rel_path = rel_path.lstrip(".")

            # Check if file should be ignored
            should_ignore = False
            for pattern in self.ignored_patterns:
                if Path(rel_path).match(pattern):
                    should_ignore = True
                    break

            if not should_ignore:
                self.files.append(str(file_path))

    def __repr__(self):
        return "\n".join(self.files[:10])
