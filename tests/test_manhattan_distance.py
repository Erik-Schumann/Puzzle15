"""Unit tests for ManhattanDistance."""

import unittest

from ManhattanDistance import ManhattanDistance
from Node import Node


class TestManhattanDistance(unittest.TestCase):
    """Tests for the Manhattan-distance heuristic."""

    def setUp(self):
        """Create a fresh heuristic instance for each test."""
        self.heuristic = ManhattanDistance()

    def test_goal_state_has_zero_distance(self):
        """The solved board has zero total displacement."""
        node = Node([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
        self.assertEqual(self.heuristic.get_heuristic(node), 0)

    def test_single_swap_of_adjacent_tiles_counts_two(self):
        """Swapping two adjacent tiles displaces each of them by one cell."""
        node = Node([[2, 1, 3], [4, 5, 6], [7, 8, 0]])
        self.assertEqual(self.heuristic.get_heuristic(node), 2)

    def test_blank_position_is_not_counted(self):
        """The blank itself contributes no distance; only the displaced tile does."""
        # Tile 8 is one cell away from its goal position; the blank is ignored.
        node = Node([[1, 2, 3], [4, 5, 6], [7, 0, 8]])
        self.assertEqual(self.heuristic.get_heuristic(node), 1)

    def test_works_for_a_2x2_board(self):
        """The heuristic is size-agnostic and works on a 2x2 board too."""
        self.assertEqual(self.heuristic.get_heuristic(Node([[1, 2], [3, 0]])), 0)
        self.assertEqual(self.heuristic.get_heuristic(Node([[0, 2], [3, 1]])), 2)


if __name__ == "__main__":
    unittest.main()
