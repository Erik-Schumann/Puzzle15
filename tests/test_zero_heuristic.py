"""Unit tests for ZeroHeuristic."""

import unittest

from Node import Node
from ZeroHeuristic import ZeroHeuristic


class TestZeroHeuristic(unittest.TestCase):
    """Tests for the zero heuristic."""

    def setUp(self):
        """Create a fresh heuristic instance for each test."""
        self.heuristic = ZeroHeuristic()

    def test_goal_state_returns_zero(self):
        """The solved board estimates zero, like every other state."""
        node = Node([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
        self.assertEqual(self.heuristic.get_heuristic(node), 0)

    def test_scrambled_state_still_returns_zero(self):
        """A far-from-goal board also estimates zero, regardless of state."""
        node = Node([[2, 1, 3], [4, 5, 6], [7, 0, 8]])
        self.assertEqual(self.heuristic.get_heuristic(node), 0)

    def test_works_for_a_2x2_board(self):
        """The heuristic is size-agnostic and works on a 2x2 board too."""
        self.assertEqual(self.heuristic.get_heuristic(Node([[1, 2], [3, 0]])), 0)
        self.assertEqual(self.heuristic.get_heuristic(Node([[0, 2], [3, 1]])), 0)


if __name__ == "__main__":
    unittest.main()
