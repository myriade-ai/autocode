#!/usr/bin/env python3
"""
Script to display folder structure,
and aggregate all file contents into one big text with headings.
"""

import logging
import sys
from pathlib import Path

from autocode.directory_utils import list_non_gitignore_files

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

LONG_FILE_THRESHOLD = 1_000  # A file with more than 1000 lines is considered long
TOKEN_LIMIT_WARNING = 128_000  # Warning threshold for token count
CHARS_PER_TOKEN = 4  # Approximation of characters per token


def build_tree_structure(root_dir: Path, tracked_files: set):
    """
    Recursively build a nested dictionary representing the folder structure
    of git-tracked files only.
    """
    tree = {}
    for item in sorted(root_dir.iterdir()):
        if item.is_file():
            if item in tracked_files:
                tree[item.name] = None
        elif item.is_dir() and item.name != ".git":
            subtree = build_tree_structure(item, tracked_files)
            if subtree:
                tree[item.name] = subtree
    return tree


def print_tree_structure(tree: dict, prefix: str = ""):
    """
    Print a bullet-like structure:
    - fileA
    - folder
       - fileB
    """
    for name, subtree in tree.items():
        yield f"{prefix}- {name}"
        if isinstance(subtree, dict):
            # Recurse deeper for subfolders
            yield from print_tree_structure(subtree, prefix + "   ")


def collect_files_content(root_dir: Path, tracked_files: set):
    """
    Recursively collect content of git-tracked files only.
    Shows "compiled - X lines" for long files.
    Skips .lock files entirely.
    """
    file_contents = []

    for filepath in tracked_files:
        # Skip .lock files entirely
        if filepath.suffix == ".lock":
            continue

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                line_count = len(content.splitlines())
                if line_count > LONG_FILE_THRESHOLD:
                    content = f"compiled - {line_count} lines"
            rel_path = filepath.relative_to(root_dir)
            file_contents.append((rel_path, content))
        except Exception as e:
            logger.error(f"Skipping file {filepath} due to error: {e}")
            continue

    return sorted(file_contents)


def estimate_token_count(text: str) -> int:
    """
    Estimate the token count of a text using a simple character-based approximation.
    Uses 4 characters per token as a rough approximation.
    """
    return len(text) // CHARS_PER_TOKEN


def prepare_export(directory: str):
    """
    Prepare the export of a directory.
    """
    repo_path = Path(directory).resolve()
    print(f"Preparing export of {repo_path}")
    tracked_files = {Path(f) for f in list_non_gitignore_files(str(repo_path))}
    print(f"Found {len(tracked_files)} tracked files")
    export = f"Export of {repo_path}\n\n"

    export += "Folder structure:\n"
    tree = build_tree_structure(repo_path, tracked_files)
    export += "\n".join(print_tree_structure(tree))

    export += "\nAggregated file contents:\n"
    files = collect_files_content(repo_path, tracked_files)
    for rel_path, content in files:
        export += f"\n### file: {rel_path}\n"
        export += content

    # Estimate token count
    token_count = estimate_token_count(export)
    logger.info(
        f"--- Export Statistics ---\nCharacters: {len(export)}\nEstimated tokens: {token_count} (using {CHARS_PER_TOKEN} chars/token approximation)"
    )

    if token_count > TOKEN_LIMIT_WARNING:
        logger.warning(
            f"⚠️ WARNING: The export exceeds {TOKEN_LIMIT_WARNING:,} tokens (estimated {token_count:,}). This may be too large for some language models to process."
        )
    return export


def main():
    if len(sys.argv) < 2:
        logger.error(f"Usage: {sys.argv[0]} <clone_dir>")
        sys.exit(1)

    clone_dir = sys.argv[1]
    export = prepare_export(clone_dir)
    with open(f"{clone_dir}.dump", "w") as f:
        f.write(export)


if __name__ == "__main__":
    main()
