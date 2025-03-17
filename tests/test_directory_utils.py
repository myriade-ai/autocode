import os

import pytest

from autocode.directory_utils import list_non_gitignore_files


@pytest.fixture
def temp_directory(tmp_path):
    """Create a temporary directory with some test files and .gitignore files"""
    # Create test files
    (tmp_path / "file1.txt").write_text("content")
    (tmp_path / "file2.py").write_text("content")

    # Create a subdirectory with files
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "subfile1.txt").write_text("content")
    (subdir / "subfile2.py").write_text("content")

    # Create ignored directory and files
    venv = tmp_path / ".venv"
    venv.mkdir()
    (venv / "bin").mkdir()
    (venv / "bin" / "activate").write_text("content")

    # Create .git directory (should be ignored)
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("content")

    # Create .gitignore file in root
    root_gitignore_content = """
# Python virtual environment
.venv/

# Python cache files
__pycache__

# Specific files to ignore
file2.py

# Test folders
ignored_folder
ignored_folder_with_slash/
"""
    (tmp_path / ".gitignore").write_text(root_gitignore_content.strip())

    # Create ignored folders
    ignored_folder = tmp_path / "ignored_folder"
    ignored_folder.mkdir()
    (ignored_folder / "ignored_file.txt").write_text("content")

    ignored_folder_with_slash = tmp_path / "ignored_folder_with_slash"
    ignored_folder_with_slash.mkdir()
    (ignored_folder_with_slash / "ignored_file.txt").write_text("content")
    # Create .gitignore file in subdirectory
    subdir_gitignore_content = """
# Ignore Python files in this subdirectory
*.py
"""
    (subdir / ".gitignore").write_text(subdir_gitignore_content.strip())

    return tmp_path


def test_list_non_gitignore_files(temp_directory):
    """Test that files are correctly filtered based on .gitignore patterns"""
    files = list_non_gitignore_files(str(temp_directory))

    # Convert paths to relative and normalize them
    rel_files = [os.path.relpath(f, str(temp_directory)) for f in files]
    rel_files = [f.replace(os.sep, "/") for f in rel_files]

    # Expected files (not ignored by .gitignore)
    expected_files = {
        "file1.txt",
        "subdir/subfile1.txt",
        ".gitignore",
        "subdir/.gitignore",
    }

    assert set(rel_files) == expected_files


def test_subdirectory_gitignore(temp_directory):
    """Test that subdirectory .gitignore files are respected"""
    subdir = temp_directory / "subdir"

    # Create a new file in the subdirectory that should not be ignored
    (subdir / "not_ignored.txt").write_text("content")

    files = list_non_gitignore_files(str(temp_directory))

    # Convert paths to relative and normalize them
    rel_files = [os.path.relpath(f, str(temp_directory)) for f in files]
    rel_files = [f.replace(os.sep, "/") for f in rel_files]

    # Expected files (not ignored by root or subdirectory .gitignore)
    expected_files = {
        "file1.txt",
        "subdir/subfile1.txt",
        "subdir/not_ignored.txt",
        ".gitignore",
        "subdir/.gitignore",
    }

    assert set(rel_files) == expected_files


def test_empty_directory(tmp_path):
    """Test handling of an empty directory"""
    files = list_non_gitignore_files(str(tmp_path))
    assert files == []


def test_ignore_folders_with_and_without_slash(temp_directory):
    """Test that folders are ignored regardless of trailing slash in .gitignore"""
    files = list_non_gitignore_files(str(temp_directory))

    # Convert paths to relative and normalize them
    rel_files = [os.path.relpath(f, str(temp_directory)) for f in files]
    rel_files = [f.replace(os.sep, "/") for f in rel_files]

    # Check that neither ignored folder is in the list of files
    assert not any(f.startswith("ignored_folder") for f in rel_files)
    assert not any(f.startswith("ignored_folder_with_slash") for f in rel_files)

    # Expected files (not ignored by .gitignore)
    expected_files = {
        "file1.txt",
        "subdir/subfile1.txt",
        ".gitignore",
        "subdir/.gitignore",
    }

    assert set(rel_files) == expected_files


def test_no_gitignore(tmp_path):
    """Test behavior when no .gitignore file exists"""
    # Create a test file
    (tmp_path / "test.txt").write_text("content")

    files = list_non_gitignore_files(str(tmp_path))
    rel_files = [os.path.relpath(f, str(tmp_path)) for f in files]
    rel_files = [f.replace(os.sep, "/") for f in rel_files]

    assert set(rel_files) == {"test.txt"}


def test_git_directory_exclusion(temp_directory):
    """Test that .git directory is always excluded"""
    # Create a file in the .git directory
    git_file = temp_directory / ".git" / "test.txt"
    git_file.write_text("content")

    files = list_non_gitignore_files(str(temp_directory))

    # Convert paths to relative and normalize them
    rel_files = [os.path.relpath(f, str(temp_directory)) for f in files]
    rel_files = [f.replace(os.sep, "/") for f in rel_files]

    # Check that no files from .git directory are included
    assert not any(f.startswith(".git/") for f in rel_files)


def test_ignore_directory_in_sub_directory_exclusion(temp_directory):
    """Test that directory in sub directory is excluded"""
    # Create a __pycache__ directory for the test
    pycache_dir = temp_directory / "subdir" / "__pycache__"
    pycache_dir.mkdir(parents=True)

    # Create a file in the __pycache__ directory
    pycache_file = pycache_dir / "test.pyc"
    pycache_file.write_text("content")

    files = list_non_gitignore_files(str(temp_directory))

    # Convert paths to relative and normalize them
    rel_files = [os.path.relpath(f, str(temp_directory)) for f in files]
    rel_files = [f.replace(os.sep, "/") for f in rel_files]

    # Check that no files from __pycache__ directory are included
    assert not any(f.startswith("subdir/__pycache__") for f in rel_files)
