import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from code_editor import CodeEditor

editor = CodeEditor()
print(editor.read_file("tests/example.py"))

diff = """--- tests/example.py
+++ tests/example.py
@@ -1,2 +1,2 @@
 def hello():
-    print("Hello, World!")
+    print("Hello, Ben!")

"""
editor.apply_diff(diff)
print(editor.read_file("tests/example.py"))
