import unittest
from unittest.mock import MagicMock, patch

from terminal import Terminal  # Assuming the class is named Terminal


class TestTerminal(unittest.TestCase):
    def setUp(self):
        self.terminal = Terminal()

    @patch("subprocess.run")
    def test_run_command(self, mock_run):
        # Set up the mock
        mock_process = MagicMock()
        mock_process.stdout = "Test output"
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        # Run the command
        result = self.terminal.run_command("echo 'Hello, World!'")

        # Assert that subprocess.run was called with the correct arguments
        mock_run.assert_called_once_with(
            "echo 'Hello, World!'", shell=True, capture_output=True, text=True
        )

        # Assert that the result is correct
        self.assertEqual(result, "Test output")

    @patch("subprocess.run")
    def test_run_command_error(self, mock_run):
        # Set up the mock to simulate an error
        mock_process = MagicMock()
        mock_process.stderr = "Error message"
        mock_process.returncode = 1
        mock_run.return_value = mock_process

        # Run the command
        with self.assertRaises(Exception):
            self.terminal.run_command("invalid_command")

        # Assert that subprocess.run was called with the correct arguments
        mock_run.assert_called_once_with(
            "invalid_command", shell=True, capture_output=True, text=True
        )


if __name__ == "__main__":
    unittest.main()
