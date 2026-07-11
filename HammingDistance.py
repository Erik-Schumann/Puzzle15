"""Hamming-distance heuristic for the 15-puzzle."""

from Heuristic import Heuristic


class HammingDistance(Heuristic):
    """Count of tiles that are not already in their goal position."""

    def get_heuristic(self, node):
        """Compute the number of misplaced tiles compared to the goal state."""
        size = len(node.state)

        # Define and declare how many elements can be possibly incorrect.
        misplaced = size * size

        # Iterate through every element and compare it to the goal state.
        for row in range(size):
            for col in range(size):
                # The goal value at (row, col) is its row-major position, wrapping the last cell to 0 (blank).
                goal_value = (row * size + col + 1) % (size * size)
                # If an element is in the same position as in the goal state, decrement the incorrect count.
                if node.state[row][col] == goal_value:
                    misplaced -= 1

        # Return count of incorrect tiles.
        return misplaced
