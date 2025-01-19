import pytest
import os
import json
from autocode.code_editor import CodeEditor
from autocode.code_editor_utils import apply_linter

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
        "ruff": {
            "lint.run": "onSave",
            "format.on.save": True,
            "organizeImports": True,
            "fixAll": True
        }
    }
    with open(settings_path, "w") as f:
        json.dump(settings, f)
    return settings_path

def test_auto_linting_on_edit(temp_python_file, mock_vscode_settings, monkeypatch, capsys):
    # Change the working directory to the temporary directory
    monkeypatch.chdir(temp_python_file.parent)
    
    # Create a CodeEditor instance
    editor = CodeEditor()

    # Mock the subprocess.run function to capture Ruff commands
    def mock_subprocess_run(args, **kwargs):
        print(f"Mock subprocess run: {' '.join(args)}")
        return None

    monkeypatch.setattr("subprocess.run", mock_subprocess_run)

    # Edit the file
    editor.edit_file(
        str(temp_python_file),
        line_index_start=2,
        delete_lines_count=1,
        insert_text="    print('Hello, Linted World!')"
    )

    # Capture the output
    captured = capsys.readouterr()

    # Assert that Ruff commands were called
    assert "Mock subprocess run: ruff check ." in captured.out
    assert "Mock subprocess run: ruff format ." in captured.out
    assert "Mock subprocess run: ruff --select I --fix ." in captured.out
    assert "Mock subprocess run: ruff --fix ." in captured.out

    # Check the content of the file after editing
    with open(temp_python_file, "r") as f:
        content = f.read()
    assert content.strip() == "def test_function():\n    print('Hello, Linted World!')".strip()

def test_auto_linting_not_applied_without_settings(temp_python_file, monkeypatch, capsys):
    # Change the working directory to the temporary directory
    monkeypatch.chdir(temp_python_file.parent)
    
    # Create a CodeEditor instance
    editor = CodeEditor()

    # Mock the subprocess.run function to capture Ruff commands
    def mock_subprocess_run(args, **kwargs):
        print(f"Mock subprocess run: {' '.join(args)}")
        return None

    monkeypatch.setattr("subprocess.run", mock_subprocess_run)

    # Edit the file
    editor.edit_file(
        str(temp_python_file),
        line_index_start=2,
        delete_lines_count=1,
        insert_text="    print('Hello, Unlinted World!')"
    )

    # Capture the output
    captured = capsys.readouterr()

    # Assert that no Ruff commands were called
    assert "Mock subprocess run: ruff" not in captured.out

    # Check the content of the file after editing
    with open(temp_python_file, "r") as f:
        content = f.read()
    assert content.strip() == "def test_function():\n    print('Hello, Unlinted World!')".strip()

    # Print the captured output for debugging
    print("Captured output:")
    print(captured.out)

