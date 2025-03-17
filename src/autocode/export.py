#!/usr/bin/env python3
"""
Script to display folder structure,
and aggregate all file contents into one big text with headings.
"""

import sys
from pathlib import Path

from autocode.directory_utils import list_non_gitignore_files

LONG_FILE_THRESHOLD = 10_000


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
    """
    file_contents = []

    for filepath in tracked_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                line_count = len(content.splitlines())
                if line_count > LONG_FILE_THRESHOLD or filepath.suffix == ".lock":
                    content = f"compiled - {line_count} lines"
            rel_path = filepath.relative_to(root_dir)
            file_contents.append((rel_path, content))
        except Exception as e:
            print(f"Skipping file {filepath} due to error: {e}", file=sys.stderr)
            continue

    return sorted(file_contents)


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

    return export


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <clone_dir>", file=sys.stderr)
        sys.exit(1)

    clone_dir = sys.argv[1]
    export = prepare_export(clone_dir)
    print(export)


if __name__ == "__main__":
    main()
