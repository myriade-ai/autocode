from fnmatch import fnmatch
from pathlib import Path


def _read_gitignore(gitignore_path: str) -> list:
    ignored_patterns = []

    if Path(gitignore_path).exists():
        with open(gitignore_path) as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue

                if line.endswith("/"):
                    line += "**"  # e.g. ".venv/" -> ".venv/**"

                if line.startswith("/"):
                    line = line[1:]

                # Store the pattern as-is
                ignored_patterns.append(line)
                # Also store a variant with **/ for deeper matching
                ignored_patterns.append(f"**/{line}")

    return ignored_patterns


def list_non_gitignore_files(directory: str = ".") -> list:
    """List all files in the directory, excluding those in .gitignore."""
    directory_path = Path(directory)
    gitignore_path = directory_path / ".gitignore"

    # 1. Read .gitignore patterns
    ignored_patterns = _read_gitignore(str(gitignore_path))

    # 2. Collect all files under the directory
    files = []
    for file_path in Path(directory).rglob("*"):
        if file_path.is_file() and not file_path.name.startswith("."):
            # Convert to relative path in posix format for pattern matching
            rel_path = file_path.relative_to(directory_path).as_posix()

            # Check if file should be ignored
            should_ignore = False
            for pattern in ignored_patterns:
                if fnmatch(rel_path, pattern):
                    should_ignore = True
                    break

            if not should_ignore:
                files.append(str(file_path))

    return files
