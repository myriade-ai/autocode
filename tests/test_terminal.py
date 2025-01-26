import subprocess
import unittest
from unittest.mock import MagicMock, patch

from autocode.terminal import Shell, Terminal


class TestShell(unittest.TestCase):
    def setUp(self):
        self.shell = Shell()

    @patch("subprocess.Popen")
    def test_run_quick_command(self, mock_popen):
        mock_process = MagicMock()
        mock_process.poll.side_effect = [None, 0]
        mock_process.stdout.read.side_effect = ["Hello, World!"]
        mock_process.stderr.read.return_value = ""
        mock_process.communicate.return_value = ("", "")
        mock_popen.return_value = mock_process

        result = self.shell.run_command("echo 'Hello, World!'")

        mock_popen.assert_called_once_with(
            "echo 'Hello, World!'",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        self.assertEqual(result, "Hello, World!")

    @patch("subprocess.Popen")
    @patch("time.time")
    def test_run_long_command(self, mock_time, mock_popen):
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_process.stdout.read.side_effect = ["Long", " running", " command"]
        mock_process.stderr.read.return_value = ""
        mock_popen.return_value = mock_process

        mock_time.side_effect = [0, 1, 2, 3, 4, 5, 6]

        result = self.shell.run_command("long_running_command")

        self.assertIn("Long running command", result)
        self.assertIn("Command is still running...", result)

    @patch("subprocess.Popen")
    def test_run_command_error(self, mock_popen):
        mock_process = MagicMock()
        mock_process.poll.side_effect = [None, 1]
        mock_process.stdout.read.return_value = ""
        mock_process.stderr.read.return_value = "Error message"
        mock_process.communicate.return_value = ("", "")
        mock_popen.return_value = mock_process

        result = self.shell.run_command("invalid_command")

        self.assertIn("Error message", result)


class TestTerminal(unittest.TestCase):
    def setUp(self):
        self.terminal = Terminal()

    def test_create_shell(self):
        shell = self.terminal.create_shell("test_shell")
        self.assertIsInstance(shell, Shell)
        self.assertIn("test_shell", self.terminal.shells)

    def test_close_shell(self):
        self.terminal.create_shell("test_shell")
        self.terminal.close_shell("test_shell")
        self.assertNotIn("test_shell", self.terminal.shells)

    def test_close_nonexistent_shell(self):
        with self.assertRaises(ValueError):
            self.terminal.close_shell("nonexistent_shell")
