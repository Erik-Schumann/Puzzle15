"""The 15-puzzle state space: initial state, goal test, and successor generation."""

import csv
import logging

from Action import Action
from Node import Node

logger = logging.getLogger(__name__)


class Problem:
    """The 15-puzzle: initial state, goal test, and successor generation."""

    def __init__(self, initial_state):
        """Wrap the given board state as the initial node, and precompute the board size/goal."""
        self.initial_node = Node(initial_state)
        self.size = len(initial_state)
        # Precomputed once here instead of rebuilt on every is_goal_state call.
        size = self.size
        self.goal_state = [[r * size + c + 1 for c in range(size)] for r in range(size)]
        self.goal_state[size - 1][size - 1] = 0

        logger.debug("Problem created: size=%dx%d initial_state=%s", size, size, initial_state)

    @classmethod
    def from_csv(cls, path):
        """Build a Problem from a CSV file holding the initial board configuration.

        Raises FileNotFoundError if `path` doesn't exist, and ValueError if the CSV
        isn't a square grid or doesn't contain each value 0..size*size-1 exactly once.
        """
        logger.debug("Loading puzzle from '%s'", path)
        with open(path, newline="", encoding="utf-8") as csv_file:
            rows = list(csv.reader(csv_file))

        if not rows:
            raise ValueError(f"CSV file '{path}' is empty.")

        size = len(rows)
        state = []
        for row in rows:
            if len(row) != size:
                raise ValueError(f"CSV file '{path}' must contain a square {size}x{size} grid.")
            state.append([int(value) for value in row])

        expected_values = set(range(size * size))
        found_values = {value for row in state for value in row}
        if found_values != expected_values:
            raise ValueError(
                f"CSV file '{path}' must contain each value 0..{size * size - 1} exactly once."
            )

        return cls(state)

    def get_initial_node(self):
        """Return the root node of the search."""
        return self.initial_node

    def is_goal_state(self, node):
        """Check whether the node's state matches the solved board (1..N-1 then blank)."""
        return node.state == self.goal_state

    def get_successors(self, node):
        """Generate the nodes reachable from `node` by sliding a neighbor into the blank."""
        size = self.size

        # Step 1: locate the blank (0) tile.
        blank_row, blank_col = 0, 0
        for r in range(size):
            for c in range(size):
                if node.state[r][c] == 0:
                    blank_row, blank_col = r, c

        # Step 2: compute the blank's coordinates after each possible move.
        moves = {
            Action.UP: (blank_row - 1, blank_col),
            Action.DOWN: (blank_row + 1, blank_col),
            Action.LEFT: (blank_row, blank_col - 1),
            Action.RIGHT: (blank_row, blank_col + 1),
        }

        # Step 3: for every move that stays on the board, swap the blank with that
        # neighbor in a copy of the state and wrap it in a successor node.
        successors = []
        for action, (new_row, new_col) in moves.items():
            if 0 <= new_row < size and 0 <= new_col < size:
                # A manual shallow copy of each row is enough here (and much cheaper
                # than copy.deepcopy) since every row holds only plain ints.
                new_state = [row[:] for row in node.state]
                new_state[blank_row][blank_col], new_state[new_row][new_col] = (
                    new_state[new_row][new_col],
                    new_state[blank_row][blank_col],
                )
                successors.append(Node(new_state, action, node, node.cost + 1))

        return successors
