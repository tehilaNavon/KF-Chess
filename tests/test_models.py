import unittest

from models import Position


class TestModels(unittest.TestCase):
    def test_position_equality(self):
        self.assertEqual(Position(1, 2), Position(1, 2))
        self.assertNotEqual(Position(1, 2), Position(2, 1))


if __name__ == "__main__":
    unittest.main()
