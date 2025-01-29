import unittest

from autocode.terminal import Shell, Terminal


class TestShell(unittest.TestCase):
    def setUp(self):
        self.shell = Shell()

    def test_immediate_command(self):
        """Test a command that completes immediately"""
        shell = Shell()
        result = shell.run_command("echo 'Hello, World!'")
        self.assertEqual(result.strip(), "Hello, World!")

    def test_multiline_output(self):
        """Test a command that produces multiple lines of output"""
        shell = Shell()
        result = shell.run_command("echo 'Line 1\nLine 2\nLine 3'")
        self.assertEqual(result.strip(), "Line 1\nLine 2\nLine 3")

    def test_command_with_error(self):
        """Test a command that produces stderr output"""
        shell = Shell()
        result = shell.run_command("ls nonexistentfile")
        self.assertIn("No such file or directory", result)

    def test_quick_continuous_output(self):
        """Test a command that produces multiple outputs but finishes quickly"""
        shell = Shell()
        result = shell.run_command("for i in {1..5}; do echo $i; done")
        self.assertEqual(result.strip(), "1\n2\n3\n4\n5")

    def test_long_running_command(self):
        """Test a command that takes longer than 5 seconds"""
        shell = Shell()
        shell.RETURN_TIMEOUT_SECONDS = 0.5
        result = shell.run_command("for i in {1..10}; do echo $i; sleep 0.1; done")
        self.assertIn("Command is still running...", result)
        # Should have some numbers but not all 20
        self.assertTrue(any(str(i) in result for i in range(1, 10)))
        # Should have at least 1-3
        self.assertTrue(all(str(i) in result for i in range(1, 4)))
        # Should not have all 10
        self.assertFalse(all(str(i) in result for i in range(1, 10)))

    def test_error_output_capture(self):
        """Test that error output is properly captured"""
        shell = Shell()
        # This command will output to both stdout and stderr
        result = shell.run_command('echo "stdout message" && echo "error message" >&2')
        self.assertIn("stdout message", result)
        self.assertIn("error message", result)


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
