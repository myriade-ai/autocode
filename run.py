from typing import Optional
import os
from autochat import Autochat


class Shell:
    """Interact with the terminal by running commands and storing history."""

    def __init__(self):
        """Initialize with empty history"""
        self.history = []

    def __repr__(self):
        """Display the command history and their outputs"""
        if not self.history:
            return "No commands executed yet"

        output = []
        for command, result in self.history[-20:]:
            output.append(f"$ {command}")
            if result:
                if len(result) > 2000:
                    result = result[:2000] + "\n...\n"
                output.append(result)

        return "\n".join(output)

    def scroll_up(self):
        """Scroll up in the terminal"""
        import subprocess

        subprocess.run(["tput", "cuu1"], shell=True)

    def scroll_down(self):
        """Scroll down in the terminal"""
        import subprocess

        subprocess.run(["tput", "cud1"], shell=True)

    def run_command(self, command):
        import subprocess

        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = result.stdout if result.stdout else result.stderr
            self.history.append((command, output))
            return output
        except Exception as e:
            error_msg = str(e)
            self.history.append((command, error_msg))
            return error_msg


class Terminal:
    """Allow to spin up shells and run commands in them."""

    def __init__(self):
        """Initialize with empty history"""
        self.shells = {}

    def __repr__(self):
        """Display the list of shells"""
        return "Shells:\n" + "\n".join(["- " + name for name in self.shells])

    def create_shell(self, name: Optional[str] = None):
        """Create a new shell"""
        shell = Shell()
        if name is None:
            # Use the shell's id as the name by default
            name = str(id(shell))
        if name in self.shells:
            raise ValueError(f"Shell {name} already exists")
        self.shells[name] = shell
        return self.shells[name]

    def close_shell(self, name: str):
        """Close a shell by its name"""
        if name not in self.shells:
            raise ValueError(f"Shell {name} does not exist")
        del self.shells[name]


class File:
    """Allow to read and write files."""

    def __init__(self, path):
        """Initialize with the file path"""
        self.path = path

    def read(self):
        """Read the file"""
        with open(self.path, "r") as file:
            return file.read()

    def write(self, content):
        """Write to the file"""
        with open(self.path, "w") as file:
            file.write(content)

    def append(self, content):
        """Append to the file"""
        with open(self.path, "a") as file:
            file.write(content)

    def delete(self):
        """Delete the file"""
        os.remove(self.path)


agent = Autochat(
    """You are an agent, which leverage tools to help you complete tasks.
    Don't answer user query, but use tools to complete the task."""
)
terminal = Terminal()
agent.add_tool(terminal)
# agent.add_tool(File)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        for message in agent.run_conversation(prompt):
            print(message.to_markdown())
    else:
        print("Please provide a prompt as command line argument")
