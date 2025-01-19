import os

import pytest

from autocode.directory_utils import list_non_gitignore_files


@pytest.fixture
def temp_directory(tmp_path):
    """Create a temporary directory with some test files and a .gitignore"""
    # Create test files
    (tmp_path / "file1.txt").write_text("content")
    (tmp_path / "file2.py").write_text("content")

    # Create a subdirectory with files
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "subfile1.txt").write_text("content")
    (subdir / "subfile2.py").write_text("content")

    # Create ignored directory and files
    venv = tmp_path / "venv"
    venv.mkdir()
    (venv / "bin").mkdir()
    (venv / "bin" / "activate").write_text("content")

    # Create .gitignore file
    gitignore_content = """
# Python virtual environment
venv/
    
# Python cache files
__pycache__/
*.pyc
    
# Specific files to ignore
file2.py
"""
    (tmp_path / ".gitignore").write_text(gitignore_content.strip())

    return tmp_path


def test_list_non_gitignore_files(temp_directory):
    """Test that files are correctly filtered based on .gitignore patterns"""
    files = list_non_gitignore_files(str(temp_directory))

    # Convert paths to relative and normalize them
    rel_files = [os.path.relpath(f, str(temp_directory)) for f in files]
    rel_files = [f.replace(os.sep, "/") for f in rel_files]

    # Expected files (not ignored by .gitignore)
    expected_files = {"file1.txt", "subdir/subfile1.txt", "subdir/subfile2.py"}

    assert set(rel_files) == expected_files


def test_empty_directory(tmp_path):
    """Test handling of an empty directory"""
    files = list_non_gitignore_files(str(tmp_path))
    assert files == []


def test_no_gitignore(tmp_path):
    """Test behavior when no .gitignore file exists"""
    # Create a test file
    (tmp_path / "test.txt").write_text("content")

    files = list_non_gitignore_files(str(tmp_path))
    rel_files = [os.path.relpath(f, str(tmp_path)) for f in files]
    rel_files = [f.replace(os.sep, "/") for f in rel_files]

    assert set(rel_files) == {"test.txt"}
