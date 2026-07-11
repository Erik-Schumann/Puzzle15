"""Manhattan-distance heuristic for the 15-puzzle."""

from Heuristic import Heuristic


class ManhattanDistance(Heuristic):
    """Sum of each tile's horizontal + vertical distance from its goal position."""

    def get_heuristic(self, node):
        """Compute the total Manhattan distance of all tiles from their goal cells."""
        state = node.state
        size = len(state)
        total = 0
        for row in range(size):
            for col in range(size):
                value = state[row][col]
                if value == 0:
                    continue
                goal_row = (value - 1) // size
                goal_col = (value - 1) % size
                total += abs(row - goal_row) + abs(col - goal_col)
        return total
