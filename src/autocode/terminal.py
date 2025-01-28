import datetime
import subprocess
import threading
import time
from queue import Empty, Queue
from typing import Optional


class Shell:
    """Interact with the terminal by running commands and storing history."""

    def __init__(self):
        """Initialize with empty history"""
        self.history = []
        self.active_process = None
        self.output_queue = None
        self.output_thread = None

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

        # Add current running command status if exists
        if self.active_process:
            current_output = self._get_current_output()
            if current_output:
                output.append("Current running command output:")
                output.append(current_output)

        return "\n".join(output)

    def scroll_up(self):
        """Scroll up in the terminal"""
        subprocess.run(["tput", "cuu1"], shell=True)

    def scroll_down(self):
        """Scroll down in the terminal"""
        subprocess.run(["tput", "cud1"], shell=True)

    def _process_output(self, process, output_queue):
        while True:
            if process.poll() is not None:
                break
            output = process.stdout.read(1)
            error = process.stderr.read(1)
            if output:
                output_queue.put(output)
            if error:
                output_queue.put(error)
        stdout, stderr = process.communicate()
        if stdout:
            output_queue.put(stdout)
        if stderr:
            output_queue.put(stderr)
        output_queue.put(None)  # Signal that the process has finished

    def run_command(self, command):
        """Run a command in the shell"""
        # Kill any existing process before starting a new one
        if self.active_process:
            self.active_process.terminate()
            self.active_process = None
            self.output_thread = None
            self.output_queue = None

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            output = ""
            self.output_queue = Queue()
            self.active_process = process

            # Start a thread to handle the process output
            self.output_thread = threading.Thread(
                target=self._process_output, args=(process, self.output_queue)
            )
            self.output_thread.start()

            start_time = time.time()
            while True:
                try:
                    chunk = self.output_queue.get(timeout=0.1)
                    if chunk is None:  # Process has finished
                        break
                    output += chunk
                except Empty:
                    pass

                if time.time() - start_time > 5:  # 5 seconds timeout
                    output += "\nCommand is still running..."
                    self.history.append((timestamp, command, output))
                    return output.strip()

            self.active_process = None
            self.history.append((timestamp, command, output))
            return output.strip()

        except Exception as e:
            error_msg = str(e)
            self.history.append((timestamp, command, error_msg))
            return error_msg

    def _get_current_output(self):
        """Get the current output of the running command"""
        if not self.active_process or not self.output_queue:
            return ""

        output = ""
        while not self.output_queue.empty():
            chunk = self.output_queue.get()
            if chunk is None:  # Process has finished
                self.active_process = None
                return output + "\nCommand has finished."
            output += chunk

        return output if output else "No new output."


class Terminal:
    """Allow to spin up shells and run commands in them."""

    def __init__(self):
        """Initialize with empty history"""
        self.shells = {}

    def __repr__(self):
        """Display the list of shells"""
        if not self.shells:
            return "No shells created yet"
        return "Available shells:\n" + "\n".join(["- " + name for name in self.shells])

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
