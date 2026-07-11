"""Unit tests for the Heuristic abstract base class."""

import unittest

from Heuristic import Heuristic


class TestHeuristic(unittest.TestCase):
    """Tests for Heuristic's abstract-method enforcement."""

    def test_cannot_be_instantiated_directly(self):
        """Heuristic itself has no concrete get_heuristic, so it can't be instantiated."""
        with self.assertRaises(TypeError):
            Heuristic()

    def test_subclass_must_implement_get_heuristic(self):
        """A subclass that skips get_heuristic is still abstract and can't be instantiated."""

        class IncompleteHeuristic(Heuristic):
            pass

        with self.assertRaises(TypeError):
            IncompleteHeuristic()


if __name__ == "__main__":
    unittest.main()
