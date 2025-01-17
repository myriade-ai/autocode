import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import Terminal

terminal = Terminal()
shell = terminal.create_shell()
shell.run_command("ls")
print(terminal)
