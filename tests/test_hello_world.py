import unittest


class TestHelloWorld(unittest.TestCase):
    def test_hello_world(self):
        """A simple hello world test"""
        self.assertEqual("hello world", "hello world")

    def test_hello_world_case_sensitive(self):
        """Test that hello world is case sensitive"""
        self.assertNotEqual("hello world", "Hello World")

    def test_hello_world_concatenation(self):
        """Test string concatenation for hello world"""
        hello = "hello"
        world = "world"
        self.assertEqual(f"{hello} {world}", "hello world")

    def test_hello_world_reversal(self):
        """Test string reversal for hello world"""
        hello_world = "hello world"
        reversed_hello_world = hello_world[::-1]
        self.assertEqual(reversed_hello_world, "dlrow olleh")


if __name__ == "__main__":
    unittest.main()
