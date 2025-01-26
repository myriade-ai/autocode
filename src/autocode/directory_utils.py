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
    """List all files in the directory, excluding those in .gitignore, .git/, and .gitignore files themselves."""
    directory_path = Path(directory).resolve()

    def should_ignore(file_path: Path, gitignore_patterns: dict) -> bool:
        for parent in file_path.parents:
            parent_patterns = gitignore_patterns.get(str(parent), [])
            rel_path = file_path.relative_to(parent).as_posix()
            for pattern in parent_patterns:
                if pattern.endswith("/"):
                    # If the pattern ends with '/', match it as a directory
                    if fnmatch(rel_path, pattern) or fnmatch(rel_path, f"{pattern}**"):
                        return True
                elif fnmatch(rel_path, pattern) or rel_path.startswith(f"{pattern}/"):
                    return True
            if rel_path.startswith(".git/"):
                return True
        return False

    # Collect all .gitignore files and their patterns
    gitignore_patterns = {}
    for gitignore_file in directory_path.rglob(".gitignore"):
        patterns = _read_gitignore(str(gitignore_file))
        gitignore_patterns[str(gitignore_file.parent)] = patterns

    # Add .git/ to ignored patterns for the root directory
    root_patterns = gitignore_patterns.get(str(directory_path), [])
    root_patterns.extend([".git/", "**/.git/"])
    gitignore_patterns[str(directory_path)] = root_patterns

    # Collect all files under the directory
    files = []
    for file_path in directory_path.rglob("*"):
        if file_path.is_file():
            if not should_ignore(file_path, gitignore_patterns):
                files.append(str(file_path))

    return files
