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
        self.long_running_processes = {}

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
        subprocess.run(["tput", "cuu1"], shell=True)

    def scroll_down(self):
        """Scroll down in the terminal"""
        subprocess.run(["tput", "cud1"], shell=True)

    def _process_output(self, process, command_id, output_queue):
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
            output_queue = Queue()
            command_id = id(process)

            # Start a thread to handle the process output
            thread = threading.Thread(
                target=self._process_output, args=(process, command_id, output_queue)
            )
            thread.start()

            start_time = time.time()
            is_long_running = False
            while True:
                try:
                    # Wait for output with a timeout
                    chunk = output_queue.get(timeout=0.1)
                    if chunk is None:  # Process has finished
                        break
                    output += chunk
                except Empty:
                    pass

                if time.time() - start_time > 5:  # 5 seconds timeout
                    # Don't terminate, just stop waiting
                    is_long_running = True
                    break

            if is_long_running:
                self.long_running_processes[command_id] = (
                    process,
                    thread,
                    output_queue,
                )
                output += "\nCommand is still running..."
            else:
                # Ensure we've collected all output
                while not output_queue.empty():
                    chunk = output_queue.get()
                    if chunk is None:
                        break
                    output += chunk

            self.history.append((timestamp, command, output))
            return output.strip()
        except Exception as e:
            error_msg = str(e)
            self.history.append((timestamp, command, error_msg))
            return error_msg

    def get_long_running_command_output(self, command_id):
        """Get the current output of a long-running command"""
        if command_id not in self.long_running_processes:
            return "Command not found or has finished."

        process, thread, output_queue = self.long_running_processes[command_id]
        output = ""
        while not output_queue.empty():
            chunk = output_queue.get()
            if chunk is None:  # Process has finished
                del self.long_running_processes[command_id]
                return output + "Command has finished."
            output += chunk

        return output if output else "No new output."


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
