import os

from autocode.code_editor import edit_file


class TestEditFile:
    def setup_method(self):
        self.filename = "example.txt"
        # Create a test file with multiple lines
        with open(self.filename, "w") as f:
            f.write("This is line 1\n")
            f.write("This is line 2\n")
            f.write("This is line 3\n")
            f.write("This is line 4\n")

    def teardown_method(self):
        # Clean up: remove the file after each test
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_edit_file_remove_lines_and_insert(self):
        # Call the edit_file function we defined above (or from your module)
        edit_file(
            filename=self.filename,
            line_index_start=2,
            delete_lines_count=2,
            insert_text="This is new line 2\nThis is new line 3",
        )

        # Verify the changes
        with open(self.filename, "r") as f:
            content = f.read().splitlines()

        expected = [
            "This is line 1",
            "This is new line 2",
            "This is new line 3",
            "This is line 4",
        ]
        assert content == expected
