import datetime
import fcntl
import json
import logging
import os
import subprocess
import threading
import time
from queue import Empty, Queue
from typing import Optional

logger = logging.getLogger(__name__)


class Shell:
    """Interact with the terminal by running commands and storing history."""

    def __init__(self):
        """Initialize with empty history"""
        self.history = []
        self.active_process = None
        self.output_queue = None
        self.output_thread = None
        self.RETURN_TIMEOUT_SECONDS = (
            5  # Maximum seconds to wait before returning partial output
        )

    def __llm__(self):
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
        """Process output from the command in a separate thread"""
        # Set non-blocking mode for stdout and stderr
        for pipe in [process.stdout, process.stderr]:
            fd = pipe.fileno()
            fl = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        def read_pipe(pipe):
            """Read from a non-blocking pipe"""
            try:
                output = pipe.read()
                if output:
                    if pipe == process.stderr:
                        return output
                    return output
                return ""
            except (IOError, TypeError):
                return ""

        while True:
            if process.poll() is not None:
                break

            # Read from both pipes
            stdout_data = read_pipe(process.stdout)
            stderr_data = read_pipe(process.stderr)

            if stdout_data:
                output_queue.put(stdout_data)
            if stderr_data:
                output_queue.put(stderr_data)

            # Small sleep to prevent CPU spinning
            time.sleep(0.001)

        # Get any remaining output
        try:
            stdout, stderr = process.communicate(timeout=0.5)
            if stdout:
                output_queue.put(stdout)
            if stderr:
                output_queue.put(stderr)
        except subprocess.TimeoutExpired:
            pass

        output_queue.put(None)  # Signal that the process has finished

    def run_command(self, command):
        """Run a command in the shell and capture its output.

        This function executes a shell command and captures its output in real-time.
        It will return early in two cases:
        1. If the command completes within 5 seconds
        2. If the command runs longer than 5 seconds or stops producing output for 0.5 seconds

        Implementation details:
        - Uses /bin/bash -c for proper shell command interpretation
        - Creates a daemon thread for output processing
        - Uses a Queue for thread-safe output transfer
        - Implements timeout mechanism of 5 seconds maximum runtime
        - Accumulates output in memory using a list for efficiency
        - Uses line buffering (bufsize=1) for real-time output
        - Captures both stdout and stderr

        Args:
            command: str, The shell command to execute

        Returns:
            str: The command's output (stdout and stderr combined).
        """
        timestamp = datetime.datetime.now()
        try:
            logger.info(f"Running command: {command}")
            process = subprocess.Popen(
                ["/bin/bash", "-c", command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True,  # Ensures proper newline handling
            )

            output = ""
            self.output_queue = Queue()
            self.active_process = process

            # Start a thread to handle the process output
            self.output_thread = threading.Thread(
                target=self._process_output,
                args=(process, self.output_queue),
                daemon=True,
            )
            self.output_thread.start()

            start_time = time.time()
            accumulated_output = []

            while True:
                if time.time() - start_time > self.RETURN_TIMEOUT_SECONDS:
                    print("Threading:", threading.enumerate())

                    # Before timing out, try to get any buffered error output
                    try:
                        _, stderr = process.communicate(timeout=0.1)
                        if stderr:
                            accumulated_output.append(stderr)
                    except subprocess.TimeoutExpired:
                        pass

                    output = "".join(accumulated_output)
                    output += "\nCommand is still running..."
                    self.history.append((timestamp, command, output))
                    return output.strip()
                try:
                    chunk = self.output_queue.get(timeout=0.1)
                    if chunk is None:  # Process has finished
                        # Get the final return code
                        return_code = process.poll()
                        self.active_process = None
                        final_output = "".join(accumulated_output)

                        # If process failed, make sure we get any final error output
                        if return_code != 0:
                            _, stderr = process.communicate()
                            if stderr:
                                final_output += stderr

                        self.history.append((timestamp, command, final_output))
                        return final_output.strip()

                    accumulated_output.append(chunk)
                except Empty:
                    pass

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

    def save_bootstrap_config(self, config: dict[str, list[str]]):
        """Save the bootstrap config in .terminal.json.
        Args:
            config: dict[str, list[str]], keys are shell names, values are lists of commands
        """
        with open(".terminal.json", "w") as f:
            json.dump(config, f, indent=2)

    def bootstrap_shells(self):
        """Setup the shells based on the config file in .terminal.json."""
        if not os.path.exists(".terminal.json"):
            raise ValueError("No config file found")

        with open(".terminal.json", "r") as f:
            config = json.load(f)

        for name, commands in config.items():
            self.create_shell(name)
            for command in commands:
                self.shells[name].run_command(command)
        logger.info(f"Boostrapped shells based on config:\n{config}")
        created_shells = [s for s in self.shells if name in config]
        logger.info(f"Created shells:\n{created_shells}")
        return created_shells
