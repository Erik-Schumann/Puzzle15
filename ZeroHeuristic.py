"""Zero heuristic for the 15-puzzle."""

from Heuristic import Heuristic


class ZeroHeuristic(Heuristic):
    """Always estimates a distance of 0, regardless of state."""

    def get_heuristic(self, node):
        """Return 0 unconditionally, making f(n) depend only on g(n)."""
        return 0
