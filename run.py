from autochat import Autochat


class Shell:
    """Interact with the terminal"""

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
    """Allow to spin up shells."""

    def __init__(self):
        """Initialize with empty history"""
        self.shells = []  

    def __repr__(self):
        """Display the command history and their outputs"""
        return "\n".join([str(t) for t in self.shells])

    def create_shell(self):
        """Create a new shell"""
        self.shells.append(Shell())
        return self.shells[-1]

    def close_shell(self, shell):
        """Close a shell"""
        self.shells.remove(shell)



agent = Autochat(
    """You are an agent, which leverage tools to help you complete tasks.
    You can use the following tools:
    - Terminal: spin up shells and run commands in them.
    """
)
terminal = Terminal()
agent.add_tool(terminal)




if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])

        for message in agent.run_conversation(prompt):
            print(message.to_markdown())
    else:
        print("Please provide a prompt as command line argument")
