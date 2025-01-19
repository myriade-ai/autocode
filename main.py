import datetime
import os
from typing import Optional

from autochat import Autochat

from code_editor import CodeEditor


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
        for timestamp, command, result in self.history[-20:]:
            output.append(f"{timestamp} $ {command}")
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

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = result.stdout if result.stdout else result.stderr
            self.history.append((timestamp, command, output))
            return f"{timestamp} $ {command}\n{output}"
        except Exception as e:
            error_msg = str(e)
            self.history.append((timestamp, command, error_msg))
            return f"{timestamp} $ {command}\n{error_msg}"


class Terminal:
    """Allow to spin up shells and run commands in them."""

    def __init__(self):
        """Initialize with empty history"""
        self.shells = {}

    def __repr__(self):
        """Display the list of shells"""
        return "Shells:\n" + "\n".join(["- " + name for name in self.shells])

    def repr(self):  # Hack to allow for shell.repr()
        """Display the list of shells"""
        return self.__repr__()

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


class InsightfulAutochat(Autochat):
    """Extension of Autochat that can store and retrieve insights."""

    def __init__(self, instructions, *args, **kwargs):
        super().__init__(instructions, *args, **kwargs)
        self.insights_file = "insights.txt"
        self.insights = self._load_insights()
        self._update_instructions()
        self.add_function(self.store_insight)

    def _load_insights(self):
        """Load insights from the file"""
        try:
            with open(self.insights_file, "r") as f:
                return f.read().splitlines()
        except FileNotFoundError:
            return []

    def _update_instructions(self):
        """Update the instructions with the loaded insights"""
        insights_text = "\n".join(self.insights)
        self.instruction += f"\n\nInsights and Feedback:\n{insights_text}"

    def store_insight(self, insight: str):
        """Store an insight for future guide to the agent. It should be general and not specific to a task."""
        with open(self.insights_file, "a") as f:
            f.write(insight + "\n")
        self.insights.append(insight)
        self._update_instructions()
        print(f"Insight stored and instructions updated: {insight}")

    def get_insights(self):
        """Retrieve all stored insights"""
        return self.insights


# Initialize the agent with basic instructions
initial_instructions = """You are an agent, which leverage tools to help you complete tasks.
When you generate shells, you will have the ability to run commands in them.
Don't answer user query, but use tools to complete the task."""

agent = InsightfulAutochat(initial_instructions, provider="openai", model="o1")
terminal = Terminal()
agent.add_tool(terminal)
code_editor = CodeEditor()
agent.add_tool(code_editor)
# agent.add_tool(File)


if __name__ == "__main__":
    import sys

    while True:
        try:
            if len(sys.argv) > 1:
                prompt = " ".join(sys.argv[1:])
            else:
                prompt = input("Enter your prompt (Ctrl+C to exit): ")

            if not prompt.strip():
                print("Please provide a prompt")
                continue

            for message in agent.run_conversation(prompt):
                print(message.to_markdown())

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
