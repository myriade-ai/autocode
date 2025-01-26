import unittest
from unittest.mock import MagicMock, patch

from autocode.terminal import Terminal, Shell  # Update the import path as needed


class TestShell(unittest.TestCase):
    def setUp(self):
        self.shell = Shell()

    @patch("subprocess.Popen")
    def test_run_quick_command(self, mock_popen):
        # Set up the mock
        mock_process = MagicMock()
        mock_process.poll.return_value = 0
        mock_process.communicate.return_value = ("Hello, World!", "")
        mock_popen.return_value = mock_process

        # Run the command
        result = self.shell.run_command("echo 'Hello, World!'")

        # Assert that subprocess.Popen was called with the correct arguments
        mock_popen.assert_called_once_with(
            "echo 'Hello, World!'", shell=True, stdout=-1, stderr=-1, text=True
        )

        # Assert that the result contains the expected output
        self.assertIn("Hello, World!", result)

    @patch("subprocess.Popen")
    @patch("time.time")
    def test_run_long_command(self, mock_time, mock_popen):
        # Set up the mocks
        mock_process = MagicMock()
        mock_process.poll.side_effect = [None, None, None, None]
        mock_process.stdout.read.side_effect = ["Test", "", "", ""]
        mock_process.stderr.read.return_value = ""
        mock_popen.return_value = mock_process

        # Simulate time passing
        mock_time.side_effect = [0, 1, 2, 3, 4, 5, 6]

        # Run the command
        result = self.shell.run_command(
            "echo 'Test' && sleep 10 && echo 'This should not be printed'"
        )

        # Assert that subprocess.Popen was called with the correct arguments
        mock_popen.assert_called_once_with(
            "echo 'Test' && sleep 10 && echo 'This should not be printed'",
            shell=True,
            stdout=-1,
            stderr=-1,
            text=True,
        )

        # Assert that the result contains the expected output
        self.assertIn("Test", result)
        self.assertIn("Command is still running...", result)
        self.assertNotIn("This should not be printed", result)

    @patch("subprocess.Popen")
    def test_run_command_error(self, mock_popen):
        # Set up the mock to simulate an error
        mock_process = MagicMock()
        mock_process.poll.return_value = 1
        mock_process.communicate.return_value = ("", "Error message")
        mock_popen.return_value = mock_process

        # Run the command
        result = self.shell.run_command("invalid_command")

        # Assert that subprocess.Popen was called with the correct arguments
        mock_popen.assert_called_once_with(
            "invalid_command", shell=True, stdout=-1, stderr=-1, text=True
        )

        # Assert that the result contains the error message
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


if __name__ == "__main__":
    unittest.main()

    def test_close_shell(self):
        self.terminal.create_shell("test_shell")
        self.terminal.close_shell("test_shell")
        self.assertNotIn("test_shell", self.terminal.shells)

    def test_close_nonexistent_shell(self):
        with self.assertRaises(ValueError):
            self.terminal.close_shell("nonexistent_shell")


if __name__ == "__main__":
    unittest.main()
