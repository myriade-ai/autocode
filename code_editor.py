class CodeEditor:
    def __init__(self):
        self.files = {}

    def read_file(
        self, filename: str, start_line: int = 1, end_line: int = None
    ) -> str:
        """Read a file with line numbers"""
        with open(filename, "r") as file:
            lines = file.read().splitlines()

        end_line = end_line or len(lines)

        display = []
        max_line_num_width = len(str(end_line))

        for i, line in enumerate(lines[start_line - 1 : end_line], start=start_line):
            line_num = str(i).rjust(max_line_num_width)
            display.append(f"{line_num} | {line}")

        return "\n".join(display)

    def apply_diff(self, diff_text: str) -> str:
        """Apply a diff to the file and return the new content and affected lines."""
        import subprocess
        import tempfile
        import os

        # FIX: diff_text should end with a newline
        if not diff_text.endswith("\n"):
            diff_text += "\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".patch", delete=False) as f:
            diff_file = f.name
            f.write(diff_text)

        # Apply the patch using git
        try:
            subprocess.run(
                [
                    "git",
                    "apply",
                    diff_file,
                ],
                check=True,
            )
        finally:
            # Clean up temporary files
            os.unlink(diff_file)


if __name__ == "__main__":
    editor = CodeEditor()
    print(editor.read_file("example.py"))

    diff = """--- example.py
+++ example.py
@@ -1,2 +1,2 @@
 def hello():
-    print("Hello, World!")
+    print("Hello, Ben!"))

"""
    editor.apply_diff(diff)
    print(editor.read_file("example.py"))
