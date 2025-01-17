import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from code_editor import CodeEditor

editor = CodeEditor()
print(editor.read_file("tests/example.py"))

diff = """--- forkSrcPrefix/tests/example.py
+++ forkDstPrefix/tests/example.py
@@ -1,2 +1,2 @@
 def hello():
-    print("Hello, World!")
+    print("Hello, Ben!")

"""
print(editor.apply_diff(diff))
print(editor.read_file("tests/example.py"))

# # Now tests errors (it shouldn't work twice)
# print(editor.apply_diff(diff))
# print(editor.read_file("tests/example.py"))

# Reset the file
with open("tests/example.py", "w") as f:
    f.write('def hello():\n    print("Hello, World!")\n')
