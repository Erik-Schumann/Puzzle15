"""Unit tests for Problem."""

import os
import tempfile
import unittest

from Action import Action
from Node import Node
from Problem import Problem


class TestProblem(unittest.TestCase):
    """Tests for Problem's state space, goal test, successors, and CSV loading."""

    def test_init_wraps_initial_state_and_records_size(self):
        """The constructor wraps the given state as the initial node and records its size."""
        problem = Problem([[1, 2], [3, 0]])
        self.assertEqual(problem.size, 2)
        self.assertEqual(problem.get_initial_node().state, [[1, 2], [3, 0]])

    def test_is_goal_state_true_for_solved_board(self):
        """A board in row-major order with the blank last is the goal state."""
        problem = Problem([[1, 2], [3, 0]])
        self.assertTrue(problem.is_goal_state(problem.get_initial_node()))

    def test_is_goal_state_false_for_unsolved_board(self):
        """Any board that doesn't match the solved layout is not a goal state."""
        problem = Problem([[1, 2], [3, 0]])
        self.assertFalse(problem.is_goal_state(Node([[0, 2], [3, 1]])))

    def test_get_successors_from_corner_blank(self):
        """A blank in a corner can only move in the two directions that stay on the board."""
        problem = Problem([[0, 2], [3, 1]])
        successors = problem.get_successors(Node([[0, 2], [3, 1]]))
        actions = {successor.action for successor in successors}
        self.assertEqual(actions, {Action.DOWN, Action.RIGHT})

    def test_get_successors_from_middle_blank(self):
        """A blank with all four neighbors on the board yields four successors."""
        state = [[1, 2, 3], [4, 0, 6], [7, 8, 5]]
        problem = Problem(state)
        successors = problem.get_successors(Node(state))
        actions = {successor.action for successor in successors}
        self.assertEqual(actions, {Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT})

    def test_get_successors_sets_predecessor_and_cost(self):
        """Every successor points back to its parent node with cost = parent.cost + 1."""
        node = Node([[0, 2], [3, 1]], cost=4)
        problem = Problem([[0, 2], [3, 1]])
        for successor in problem.get_successors(node):
            self.assertIs(successor.predecessor, node)
            self.assertEqual(successor.cost, 5)

    def _write_csv(self, text):
        """Write `text` to a temporary CSV file and return its path, cleaned up after the test."""
        csv_file = tempfile.NamedTemporaryFile(
            "w", suffix=".csv", delete=False, newline=""
        )
        csv_file.write(text)
        csv_file.close()
        self.addCleanup(os.remove, csv_file.name)
        return csv_file.name

    def test_from_csv_builds_matching_problem(self):
        """A well-formed CSV file produces a Problem wrapping the matching board."""
        path = self._write_csv("1,2\n3,0\n")
        problem = Problem.from_csv(path)
        self.assertEqual(problem.get_initial_node().state, [[1, 2], [3, 0]])

    def test_from_csv_missing_file_raises_file_not_found_error(self):
        """A nonexistent path raises the standard FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            Problem.from_csv("does_not_exist_puzzle15.csv")

    def test_from_csv_non_square_grid_raises_value_error(self):
        """A CSV whose rows aren't all the same length as the row count raises ValueError."""
        path = self._write_csv("1,2,3\n4,0\n")
        with self.assertRaises(ValueError):
            Problem.from_csv(path)

    def test_from_csv_duplicate_values_raise_value_error(self):
        """A CSV missing a required tile value (here duplicating 1) raises ValueError."""
        path = self._write_csv("1,1\n3,0\n")
        with self.assertRaises(ValueError):
            Problem.from_csv(path)

    def test_from_csv_non_integer_value_raises_value_error(self):
        """A CSV cell that isn't an integer raises ValueError."""
        path = self._write_csv("1,x\n3,0\n")
        with self.assertRaises(ValueError):
            Problem.from_csv(path)


if __name__ == "__main__":
    unittest.main()
