import pytest
import os
from unittest.mock import patch
from autocode.code_editor import CodeEditor


@pytest.fixture
def temp_dir(tmpdir):
    return str(tmpdir)


@pytest.fixture
def code_editor(temp_dir):
    return CodeEditor(temp_dir)


def test_search_files_with_match(code_editor, temp_dir):
    file_content = (
        "This is a test file\nwith multiple lines\nand some content to search for."
    )
    file_path = os.path.join(temp_dir, "test_file.txt")
    with open(file_path, "w") as f:
        f.write(file_content)

    expected_result = "> test_file.txt\n  Line 3: and some content to search for."

    with patch(
        "autocode.directory_utils.list_non_gitignore_files",
        return_value=["test_file.txt"],
    ):
        result = code_editor.search_files("content to search")
        assert result == expected_result


def test_search_files_no_match(code_editor, temp_dir):
    file_content = "This is a test file\nwith multiple lines\nbut no matching content."
    file_path = os.path.join(temp_dir, "test_file.txt")
    with open(file_path, "w") as f:
        f.write(file_content)

    with patch(
        "autocode.directory_utils.list_non_gitignore_files",
        return_value=["test_file.txt"],
    ):
        result = code_editor.search_files("nonexistent content")
        assert result == ""


def test_search_files_multiple_matches(code_editor, temp_dir):
    file_content = "This is a test file\nwith multiple lines\nand some content to search for.\nAnother line with content."
    file_path = os.path.join(temp_dir, "test_file.txt")
    with open(file_path, "w") as f:
        f.write(file_content)

    expected_result = "> test_file.txt\n  Line 3: and some content to search for.\n  Line 4: Another line with content."

    with patch(
        "autocode.directory_utils.list_non_gitignore_files",
        return_value=["test_file.txt"],
    ):
        result = code_editor.search_files("content")
        assert result == expected_result


def test_search_files_case_insensitive(code_editor, temp_dir):
    file_content = "This is a test file\nwith UPPERCASE content\nand lowercase content."
    file_path = os.path.join(temp_dir, "test_file.txt")
    with open(file_path, "w") as f:
        f.write(file_content)

    expected_result = "> test_file.txt\n  Line 2: with UPPERCASE content\n  Line 3: and lowercase content."

    with patch(
        "autocode.directory_utils.list_non_gitignore_files",
        return_value=["test_file.txt"],
    ):
        result = code_editor.search_files("content")
        assert result == expected_result
