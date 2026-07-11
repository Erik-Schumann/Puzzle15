"""A puzzle-search tree node."""

import logging

logger = logging.getLogger(__name__)


class Node:
    """A single puzzle state, the action that produced it, and a link to its predecessor."""

    def __init__(self, state, action=None, predecessor=None, cost=0):
        """Store the board state, the action that led to it, its predecessor node, and its cost."""
        self.state = state
        self.action = action
        self.predecessor = predecessor
        self.cost = cost
        # The state never changes after construction, so the hash can be computed once
        # here instead of on every hash(node) call (push and pop each call it at least once).
        self._hash = hash(tuple(tuple(row) for row in state))

    def __hash__(self):
        """Hash of the board state, used as the visited-set key."""
        return self._hash

    def path_cost(self):
        """g(n): number of moves from the initial node to this node."""
        return self.cost

    def __str__(self):
        """Format the action that led to this node and its board state for logging/printing."""
        rows = "\n".join(" ".join(f"{val:2}" for val in row) for row in self.state)
        action_str = self.action.value if self.action else "None"
        return f"Action: {action_str}\n{rows}"

    def print_history(self):
        """Log the full path from the root node to this node, oldest first, at INFO level."""
        # Step 1: recurse into the predecessor first so older nodes log before newer ones.
        if self.predecessor is not None:
            self.predecessor.print_history()
        # Step 2: log this node after its ancestors.
        logger.info("%s", self)
