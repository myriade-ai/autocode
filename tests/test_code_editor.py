import os
import shutil

import pytest
from PIL import UnidentifiedImageError

# If your CodeEditor class is in a file named code_editor.py, adjust as needed:
from autocode.code_editor import CodeEditor

print(UnidentifiedImageError)


@pytest.fixture(autouse=True)
def set_autochat_env():
    """
    This fixture automatically runs before each test.
    It sets an environment variable required by CodeEditor.
    """
    os.environ["AUTOCHAT_OUTPUT_SIZE_LIMIT"] = "1000"
    yield
    # Cleanup or unset if needed
    del os.environ["AUTOCHAT_OUTPUT_SIZE_LIMIT"]


def test_read_file_text(tmp_path):
    """
    Test reading a text file with line numbering.
    """
    # Arrange
    test_file = tmp_path / "hello.txt"
    test_file_content = """Hello, World!
This is a test file.
It has multiple lines.
"""
    test_file.write_text(test_file_content)
    test_file_abspath = os.path.abspath(test_file)
    # Initialize CodeEditor with the temporary directory
    editor = CodeEditor(directory=tmp_path)
    file_output = editor.read_file(test_file_abspath)

    # Assert
    # Check that line numbering and content appear correctly
    assert "line number|line content" in file_output
    assert "---|---" in file_output
    assert "Hello, World!" in file_output
    assert "It has multiple lines." in file_output
    # Ensure the file is considered "open"
    assert test_file_abspath in editor.open_files


def test_read_file_partial_lines(tmp_path):
    """
    Test reading only a subset of lines (start_line, end_line).
    """
    # Arrange
    test_file = tmp_path / "partial.txt"
    content_lines = ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5"]
    test_file.write_text("\n".join(content_lines))

    editor = CodeEditor(directory=str(tmp_path))

    test_file_abspath = os.path.abspath(test_file)
    file_output = editor.read_file(test_file_abspath, start_line=2, end_line=4)

    # Assert
    # Check that only lines 2,3,4 appear
    assert "Line 1" not in file_output
    assert "Line 2" in file_output
    assert "Line 3" in file_output
    assert "Line 4" in file_output
    assert "Line 5" not in file_output


def test_edit_file_delete_and_insert(tmp_path):
    """
    Test deleting and inserting lines in a file.
    """
    # Arrange
    test_file = tmp_path / "test_edit.txt"
    original_content = """Line 1
Line 2
Line 3
Line 4
Line 5
"""
    test_file.write_text(original_content)

    editor = CodeEditor(directory=str(tmp_path))

    # We expect to remove line 2 and 3, and insert new text at line 2
    insert_text = "Inserted line\nInserted line 2"

    # Act
    # 1) line_index_start=2, delete_lines_count=2 -> remove lines 2 and 3
    # 2) insert the multi-line `insert_text
    test_file_abspath = os.path.abspath(test_file)
    updated_output = editor.edit_file(
        path=test_file_abspath,
        line_index_start=2,
        delete_lines_count=2,
        insert_text=insert_text,
    )

    # Assert
    # The file after editing should have lines:
    # Line 1
    # Inserted line
    # Inserted line 2
    # Line 4
    # Line 5
    # Check the final contents by reading again
    print("test_file_abspath", test_file_abspath)
    final_content = editor.read_file(test_file_abspath)
    assert "Line 2" not in final_content
    assert "Line 3" not in final_content
    assert "Inserted line" in final_content
    assert "Inserted line 2" in final_content
    assert "Line 4" in final_content
    assert "Line 5" in final_content

    print("updated_output", updated_output)
    # The returned updated_output is a *truncated context* in the code,
    # so we only check that it contains some snippet of the replaced text
    assert "Inserted line" in updated_output
    assert "Inserted line 2" in updated_output


def test_edit_file_boundaries(tmp_path):
    """
    Test that edit_file raises appropriate errors for out-of-bound line indices.
    """
    current_test_directory = os.path.dirname(os.path.abspath(__file__))
    lorem_file = os.path.join(current_test_directory, "lorem.txt")
    test_file = tmp_path / "lorem.txt"
    test_file_abspath = os.path.abspath(test_file)
    # copy the file to the tmp_path
    shutil.copy(lorem_file, test_file)

    editor = CodeEditor(directory=str(tmp_path))
    # Try to start deleting out of range
    with pytest.raises(ValueError, match="Start line out of bounds"):
        editor.edit_file(test_file_abspath, line_index_start=100, delete_lines_count=1)

    # Verify edit_file output
    output = editor.edit_file(
        test_file_abspath, line_index_start=10, delete_lines_count=1, insert_text="Ok"
    )
    assert (
        """ 6|Fusce nec vestibulum mauris
 7|Donec nec odio at justo blandit rutrum quis in libero
 8|Maecenas dapibus lorem at risus pellentesque convallis
 9|Sed mattis finibus sapien, nec lobortis turpis semper quis
10|Ok
11|Praesent nec felis consectetur, auctor metus vitae, placerat sem
12|Proin commodo magna eget mauris efficitur interdum
13|Mauris sagittis, felis quis bibendum interdum, lacus risus molestie eros, id tempus eros urna vitae nunc
14|Proin nec blandit nibh, venenatis bibendum elit"""
        in output
    )


def test_str_replace(tmp_path):
    """
    Test str_replace on a file.
    """
    test_file = tmp_path / "test_str_replace.txt"
    test_file.write_text("Hello, World!")
    test_file_abspath = os.path.abspath(test_file)
    editor = CodeEditor(directory=str(tmp_path))
    editor.str_replace(test_file_abspath, "Hello", "Hi")
    # Check that the file was edited
    with open(test_file_abspath, "r") as f:
        assert f.read() == "Hi, World!"


def test_str_replace_file(tmp_path):
    """ "
    Test that str_replace raises appropriate errors
    """
    current_test_directory = os.path.dirname(os.path.abspath(__file__))
    lorem_file = os.path.join(current_test_directory, "lorem.txt")
    test_file = tmp_path / "lorem.txt"
    test_file_abspath = os.path.abspath(test_file)
    # copy the file to the tmp_path
    shutil.copy(lorem_file, test_file)

    editor = CodeEditor(directory=str(tmp_path))
    with pytest.raises(ValueError, match="Old string 'Hello' not found in file"):
        editor.str_replace(test_file_abspath, "Hello", "Hi")
