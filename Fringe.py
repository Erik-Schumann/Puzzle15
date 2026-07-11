"""The search fringe (open set), ordered by the weighted evaluation function."""

import itertools
import queue

from NoSolutionError import NoSolutionError


class Fringe:
    """Open-set for search: a priority queue ordered by f(n) = a*g(n) + b*h(n).

    Choosing a/b selects the effective search strategy: a=1,b=0 behaves like
    Dijkstra (uniform-cost search), a=0,b=1 like Greedy best-first search, a=1,b=1
    like plain A*, and a=1,b>1 like weighted A*.

    Also tracks which states have already been popped, so `pop` never returns the
    same state twice even if it was pushed onto the fringe more than once — unless
    `track_visited` is disabled, in which case states may be pushed/popped repeatedly.
    """

    def __init__(self, heuristic, a=1.0, b=1.0, track_visited=True):
        """Store the heuristic/weights and create the underlying priority queue.

        `track_visited` controls whether already-popped states are remembered and
        skipped on subsequent push/pop; disabling it allows the same state to be
        pushed and popped more than once.
        """
        self.heuristic = heuristic
        self.a = a
        self.b = b
        self.track_visited = track_visited
        self._queue = queue.PriorityQueue()
        self._counter = itertools.count()
        self._visited = set()
        self.lowest_heuristic = float("inf")
        self.max_fringe_size = 0

    def is_empty(self):
        """Whether there is anything left to explore."""
        return self._queue.empty()

    def push(self, node):
        """Add a node to the fringe, ordered by its evaluation.

        Skips (and returns False for) a node whose state has already been popped
        (unless `track_visited` is disabled); returns True if the node was actually
        inserted. Updates `max_fringe_size` with the queue's size (including any
        not-yet-discarded stale duplicates) after the insertion.
        """
        if self.track_visited and hash(node) in self._visited:
            return False
        priority = self._evaluate(node)
        self._queue.put((priority, next(self._counter), node))
        if self._queue.qsize() > self.max_fringe_size:
            self.max_fringe_size = self._queue.qsize()
        return True

    def pop(self):
        """Remove and return the next not-yet-visited node, marking it visited.

        If `track_visited` is disabled, visited-state bookkeeping is skipped
        entirely and the next node in priority order is always returned.
        Raises NoSolutionError once the fringe is exhausted without finding one.
        """
        while not self.is_empty():
            _, _, node = self._queue.get()
            if not self.track_visited:
                return node
            node_hash = hash(node)
            if node_hash not in self._visited:
                self._visited.add(node_hash)
                return node
        raise NoSolutionError("No solution exists for the given puzzle state.")

    def _evaluate(self, node):
        """f(n) = a*g(n) + b*h(n). Updates `lowest_heuristic` with h(n)."""
        if self.heuristic is None:
            raise TypeError("heuristic must not be None.")
        heuristic_value = self.heuristic.get_heuristic(node)
        if heuristic_value < self.lowest_heuristic:
            self.lowest_heuristic = heuristic_value
        return self.a * node.path_cost() + self.b * heuristic_value
