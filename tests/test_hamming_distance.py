"""Unit tests for HammingDistance."""

import unittest

from HammingDistance import HammingDistance
from Node import Node


class TestHammingDistance(unittest.TestCase):
    """Tests for the Hamming-distance heuristic."""

    def setUp(self):
        """Create a fresh heuristic instance for each test."""
        self.heuristic = HammingDistance()

    def test_goal_state_has_zero_misplaced_tiles(self):
        """The solved board has no misplaced tiles."""
        node = Node([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
        self.assertEqual(self.heuristic.get_heuristic(node), 0)

    def test_single_swap_counts_two_misplaced_tiles(self):
        """Swapping two adjacent tiles misplaces exactly both of them."""
        node = Node([[2, 1, 3], [4, 5, 6], [7, 8, 0]])
        self.assertEqual(self.heuristic.get_heuristic(node), 2)

    def test_displaced_blank_counts_both_affected_cells(self):
        """Moving the blank out of place also misplaces the tile now sitting in its slot."""
        node = Node([[1, 2, 3], [4, 5, 6], [7, 0, 8]])
        self.assertEqual(self.heuristic.get_heuristic(node), 2)

    def test_works_for_a_2x2_board(self):
        """The heuristic is size-agnostic and works on a 2x2 board too."""
        self.assertEqual(self.heuristic.get_heuristic(Node([[1, 2], [3, 0]])), 0)
        self.assertEqual(self.heuristic.get_heuristic(Node([[0, 2], [3, 1]])), 2)


if __name__ == "__main__":
    unittest.main()
