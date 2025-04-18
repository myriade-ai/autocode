import unittest


class TestSimpleMath(unittest.TestCase):
    def test_addition(self):
        """Verify that 1+1=2"""
        self.assertEqual(1 + 1, 2)


if __name__ == "__main__":
    unittest.main()
