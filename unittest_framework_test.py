import unittest

class TestClassCheck(unittest.TestCase):
    def basic_math_test(self):
        x = 3
        y =2
        self.assertEqual(x-y, 1)
        self.assertEqual(x+y, 5)

if __name__ == "__main__":
    unittest.main()