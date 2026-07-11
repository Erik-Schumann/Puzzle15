"""Unit tests for Action."""

import unittest

from Action import Action


class TestAction(unittest.TestCase):
    """Tests for the Action enum."""

    def test_members_have_expected_values(self):
        """Each member's `.value` matches its lowercase direction name."""
        self.assertEqual(Action.UP.value, "up")
        self.assertEqual(Action.DOWN.value, "down")
        self.assertEqual(Action.LEFT.value, "left")
        self.assertEqual(Action.RIGHT.value, "right")

    def test_has_exactly_four_members(self):
        """Only the four cardinal directions are defined."""
        self.assertEqual(len(Action), 4)


if __name__ == "__main__":
    unittest.main()
