import datetime
import select
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
        self.RETURN_TIMEOUT_SECONDS = (
            5  # Maximum seconds to wait before returning partial output
        )

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
        """Process output from the command in a separate thread.

        This function runs in a separate thread and continuously reads output from
        the process's stdout and stderr, putting the output into a queue for the
        main thread to consume.

        Implementation details:
        - Uses select() to check for available output without blocking
        - Runs in a separate thread to prevent blocking the main thread
        - Uses a very small sleep (0.001s) to prevent CPU spinning
        - Captures both stdout and stderr simultaneously
        - Signals completion by putting None into the queue

        Args:
            process: A subprocess.Popen object representing the running process
            output_queue: A Queue object to store the process output
        """

        def read_all_available(pipe):
            """Read all available output from a pipe without blocking.

            Uses select to check if there's data ready to be read, then reads
            all available lines from the pipe. This prevents blocking while
            waiting for output.

            Implementation details:
            - Uses select with 0 timeout for non-blocking checks
            - Reads line by line until no more data is available
            - Preserves newlines in the output
            - Returns immediately if no data is available

            Args:
                pipe: A file-like object (process stdout or stderr)

            Returns:
                str: All available output from the pipe joined into a single string
            """
            output = []
            while True:
                # Check if there's data ready to be read
                ready, _, _ = select.select([pipe], [], [], 0)
                if not ready:
                    break

                line = pipe.readline()
                if not line:
                    break
                output.append(line)
            return "".join(output)

        while True:
            if process.poll() is not None:
                break

            # Read all available output
            output = read_all_available(process.stdout)
            error = read_all_available(process.stderr)

            if output:
                output_queue.put(output)
            if error:
                output_queue.put(error)

            # Smaller sleep to check more frequently
            time.sleep(0.001)

        # Get any remaining output
        stdout, stderr = process.communicate()
        if stdout:
            output_queue.put(stdout)
        if stderr:
            output_queue.put(stderr)
        output_queue.put(None)  # Signal that the process has finished

    def run_command(self, command):
        """Run a command in the shell"""
        timestamp = datetime.datetime.now()
        try:
            print("running command", command)
            process = subprocess.Popen(
                ["/bin/bash", "-c", command],  # Use bash to interpret commands properly
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
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
                # First, process all available output
                while True:
                    try:
                        chunk = self.output_queue.get_nowait()
                        if chunk is None:  # Process has finished
                            self.active_process = None
                            self.history.append((timestamp, command, output))
                            return output.strip()
                        output += chunk
                    except Empty:
                        break  # No more output available right now

                # Then check if we've hit the timeout
                if time.time() - start_time > self.RETURN_TIMEOUT_SECONDS:
                    output += "\nCommand is still running..."
                    self.history.append((timestamp, command, output))
                    return output.strip()

                # Short sleep to prevent CPU spinning
                time.sleep(0.1)

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
