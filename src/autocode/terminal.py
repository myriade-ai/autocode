import datetime
from typing import Optional


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
        """Run a command in the shell"""
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
