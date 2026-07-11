"""Abstract base class for search heuristics."""

from abc import ABC, abstractmethod


class Heuristic(ABC):
    """Common interface for search heuristics used to estimate distance to the goal."""

    @abstractmethod
    def get_heuristic(self, node):
        """Estimate the cost from `node`'s state to the goal state."""
        raise NotImplementedError
