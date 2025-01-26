import json
import os

import pytest

from autocode.code_editor import CodeEditor


@pytest.fixture
def temp_python_file(tmp_path):
    file_path = tmp_path / "test_file.py"
    with open(file_path, "w") as f:
        f.write("def test_function():\n    print('Hello, World!')\n")
    return file_path


@pytest.fixture
def mock_vscode_settings(tmp_path):
    settings_path = tmp_path / ".vscode" / "settings.json"
    os.makedirs(settings_path.parent, exist_ok=True)
    settings = {
        "[python]": {
            "editor.formatOnSave": True,
            "editor.defaultFormatter": "charliermarsh.ruff",
            "editor.codeActionsOnSave": {
                "source.fixAll": "explicit",
                "source.organizeImports": "explicit",
            },
        }
    }
    with open(settings_path, "w") as f:
        json.dump(settings, f)
    return settings_path


def test_auto_linting_on_edit(
    temp_python_file, mock_vscode_settings, monkeypatch, capsys
):
    # Change the working directory to the temporary directory
    monkeypatch.chdir(temp_python_file.parent)

    # Create a CodeEditor instance
    editor = CodeEditor()

    # Edit the file
    editor.edit_file(
        str(temp_python_file),
        line_index_start=2,
        delete_lines_count=1,
        insert_text="    print('Hello, Linted World!')",
    )

    # Check the content of the file after editing
    with open(temp_python_file, "r") as f:
        content = f.read()
    assert (
        content.strip()
        == 'def test_function():\n    print("Hello, Linted World!")'.strip()
    )


def test_auto_linting_not_applied_without_settings(
    temp_python_file, monkeypatch, capsys
):
    # Change the working directory to the temporary directory
    monkeypatch.chdir(temp_python_file.parent)

    # Create a CodeEditor instance
    editor = CodeEditor()

    # Edit the file
    editor.edit_file(
        str(temp_python_file),
        line_index_start=2,
        delete_lines_count=1,
        insert_text="    print('Hello, Unlinted World!')",
    )

    # Check the content of the file after editing
    with open(temp_python_file, "r") as f:
        content = f.read()
    assert (
        content.strip()
        == "def test_function():\n    print('Hello, Unlinted World!')".strip()
    )
